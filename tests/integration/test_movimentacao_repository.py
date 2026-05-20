"""Integration tests for MovimentacaoRepository — TDD (RED phase).

These tests run against a real PostgreSQL database (the test database created
by the session-scoped ``db_connection`` fixture in ``conftest.py``).  No mocks
are used for the database layer.

The module ``repositories.movimentacao_repository`` does **not** exist yet; all
tests are expected to fail with ``ImportError`` or ``ModuleNotFoundError``
until the Backend Dev implements the repository.

Test naming convention:
    test_<method>_quando_<condition>_deve_<expected_result>

Structure:
    - Arrange / Act / Assert blocks separated by blank lines.
    - One assertion per test function where possible.
    - Zero business logic (no ``if``, ``for``, or computed values) inside tests.
    - Each test is independently executable; no inter-test state dependencies.

Isolation:
    Every test is wrapped in the ``db_transaction`` fixture (declared via
    ``pytestmark``) which rolls back to a savepoint after each test, restoring
    the seed state.

Foreign-key dependency:
    All movimentacao records reference ``figurinhas.id``.  The seed row BRA-1
    (inserted during session setup) provides a valid ``figurinha_id`` for the
    majority of tests.  Tests that verify FK rejection use an ID that is
    guaranteed not to exist (``999999``).
"""

import pytest
import psycopg2

from models.movimentacao import Movimentacao

# Apply savepoint-based rollback to every test in this module.
pytestmark = pytest.mark.usefixtures("db_transaction")


# ---------------------------------------------------------------------------
# Import under test — will fail with ImportError until implemented (RED).
# ---------------------------------------------------------------------------
from repositories.movimentacao_repository import MovimentacaoRepository  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — resolve the seed figurinha_id once per test via the repository.
# ---------------------------------------------------------------------------


def _seed_figurinha_id(db_connection: psycopg2.extensions.connection) -> int:
    """Return the ``id`` of the BRA-1 seed row.

    A direct SELECT is used here intentionally: this helper is not part of the
    class under test, so using it avoids a circular dependency on
    FigurinhaRepository in MovimentacaoRepository tests.

    Args:
        db_connection: Open test database connection.

    Returns:
        The integer primary key of the BRA-1 figurinha.
    """
    with db_connection.cursor() as cur:
        cur.execute("SELECT id FROM figurinhas WHERE codigo_figurinha = 'BRA-1'")
        row = cur.fetchone()
    assert row is not None, "Seed figurinha BRA-1 not found — session setup may have failed."
    return row[0]


# ===========================================================================
# insert
# ===========================================================================


def test_insert_deve_persistir_todos_os_campos(
    movimentacao_repository: MovimentacaoRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """insert must write every supplied field to the movimentacoes table.

    After inserting, a direct SELECT verifies that the stored values match the
    input arguments exactly, including the optional ``observacao`` and
    ``entrada_bruta`` fields.
    """
    figurinha_id = _seed_figurinha_id(db_connection)

    movimentacao_repository.insert(
        figurinha_id=figurinha_id,
        tipo="ENTRADA",
        quantidade=3,
        origem="MANUAL",
        observacao="Comprei num pacotinho",
        telegram_user_id=user_info["telegram_user_id"],
        telegram_username=user_info["telegram_username"],
        entrada_bruta="BRA-1 +3",
    )
    db_connection.commit()

    with db_connection.cursor() as cur:
        cur.execute(
            """
            SELECT figurinha_id, tipo, quantidade, origem, observacao,
                   telegram_user_id, telegram_username, entrada_bruta
              FROM movimentacoes
             WHERE figurinha_id = %s
             ORDER BY created_at DESC
             LIMIT 1
            """,
            (figurinha_id,),
        )
        row = cur.fetchone()

    assert row == (
        figurinha_id,
        "ENTRADA",
        3,
        "MANUAL",
        "Comprei num pacotinho",
        user_info["telegram_user_id"],
        user_info["telegram_username"],
        "BRA-1 +3",
    )


def test_insert_deve_retornar_movimentacao_com_id_preenchido(
    movimentacao_repository: MovimentacaoRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """insert must return a Movimentacao whose ``id`` is a positive integer.

    The database generates the primary key via SERIAL; the repository is
    expected to retrieve it (e.g. using ``RETURNING id``) and include it in the
    returned object.
    """
    figurinha_id = _seed_figurinha_id(db_connection)

    result = movimentacao_repository.insert(
        figurinha_id=figurinha_id,
        tipo="ENTRADA",
        quantidade=1,
        origem="MANUAL",
        observacao=None,
        telegram_user_id=user_info["telegram_user_id"],
        telegram_username=user_info["telegram_username"],
        entrada_bruta=None,
    )
    db_connection.commit()

    assert isinstance(result, Movimentacao)


def test_insert_deve_retornar_movimentacao_com_id_positivo(
    movimentacao_repository: MovimentacaoRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """insert must return a Movimentacao with an id greater than zero."""
    figurinha_id = _seed_figurinha_id(db_connection)

    result = movimentacao_repository.insert(
        figurinha_id=figurinha_id,
        tipo="ENTRADA",
        quantidade=2,
        origem="MANUAL",
        observacao=None,
        telegram_user_id=user_info["telegram_user_id"],
        telegram_username=user_info["telegram_username"],
        entrada_bruta=None,
    )
    db_connection.commit()

    assert result.id > 0


def test_insert_quando_figurinha_id_inexistente_deve_rejeitar_fk(
    movimentacao_repository: MovimentacaoRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """insert with a non-existent figurinha_id must raise a foreign-key error.

    The ``movimentacoes.figurinha_id`` column references ``figurinhas.id`` with
    ON DELETE RESTRICT; the database must reject the insert.
    """
    nonexistent_figurinha_id = 999999

    with pytest.raises((psycopg2.IntegrityError, psycopg2.DatabaseError)):
        movimentacao_repository.insert(
            figurinha_id=nonexistent_figurinha_id,
            tipo="ENTRADA",
            quantidade=1,
            origem="MANUAL",
            observacao=None,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
            entrada_bruta=None,
        )
        db_connection.commit()


def test_insert_quando_quantidade_zero_deve_rejeitar_check_constraint(
    movimentacao_repository: MovimentacaoRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """insert with quantidade=0 must raise an error due to the CHECK constraint.

    The schema enforces ``quantidade > 0`` on movimentacoes; zero is invalid.
    """
    figurinha_id = _seed_figurinha_id(db_connection)

    with pytest.raises((psycopg2.IntegrityError, psycopg2.DatabaseError)):
        movimentacao_repository.insert(
            figurinha_id=figurinha_id,
            tipo="ENTRADA",
            quantidade=0,
            origem="MANUAL",
            observacao=None,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
            entrada_bruta=None,
        )
        db_connection.commit()


def test_insert_deve_salvar_entrada_bruta_sem_modificacao(
    movimentacao_repository: MovimentacaoRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """insert must persist the raw entrada_bruta string exactly as supplied.

    No trimming, casing normalisation, or any other transformation should be
    applied to the audit field before storage.
    """
    figurinha_id = _seed_figurinha_id(db_connection)
    raw_input = "  BRA-1  +5  "

    movimentacao_repository.insert(
        figurinha_id=figurinha_id,
        tipo="ENTRADA",
        quantidade=5,
        origem="MANUAL",
        observacao=None,
        telegram_user_id=user_info["telegram_user_id"],
        telegram_username=user_info["telegram_username"],
        entrada_bruta=raw_input,
    )
    db_connection.commit()

    with db_connection.cursor() as cur:
        cur.execute(
            """
            SELECT entrada_bruta
              FROM movimentacoes
             WHERE figurinha_id = %s
             ORDER BY created_at DESC
             LIMIT 1
            """,
            (figurinha_id,),
        )
        row = cur.fetchone()

    assert row is not None and row[0] == raw_input
