"""Integration tests for FigurinhaRepository — TDD (RED phase).

These tests run against a real PostgreSQL database (the test database created
by the session-scoped ``db_connection`` fixture in ``conftest.py``).  No mocks
are used for the database layer.

The module ``repositories.figurinha_repository`` does **not** exist yet; all
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
"""

import pytest
import psycopg2

from models.figurinha import Figurinha

# Apply savepoint-based rollback to every test in this module.
pytestmark = pytest.mark.usefixtures("db_transaction")


# ---------------------------------------------------------------------------
# Import under test — will fail with ImportError until implemented (RED).
# ---------------------------------------------------------------------------
from repositories.figurinha_repository import FigurinhaRepository  # noqa: E402


# ===========================================================================
# find_by_codigo
# ===========================================================================


def test_find_by_codigo_quando_codigo_existe_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_codigo must return a Figurinha instance when the code is present.

    BRA-1 is guaranteed to exist because it is inserted as the session seed.
    """
    result = figurinha_repository.find_by_codigo("BRA-1")

    assert isinstance(result, Figurinha)


def test_find_by_codigo_quando_codigo_existe_deve_retornar_codigo_correto(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_codigo must return the Figurinha whose codigo_figurinha matches."""
    result = figurinha_repository.find_by_codigo("BRA-1")

    assert result is not None and result.codigo_figurinha == "BRA-1"


def test_find_by_codigo_quando_codigo_inexistente_deve_retornar_none(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_codigo must return None for a code that has no row in the DB."""
    result = figurinha_repository.find_by_codigo("ZZZ-99")

    assert result is None


# ===========================================================================
# find_by_par (codigo_selecao, numero)
# ===========================================================================


def test_find_by_par_quando_par_existe_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_par must return a Figurinha when (codigo_selecao, numero) matches."""
    result = figurinha_repository.find_by_par(codigo_selecao="BRA", numero=1)

    assert isinstance(result, Figurinha)


def test_find_by_par_quando_par_existe_deve_retornar_par_correto(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_par must return the Figurinha whose (codigo_selecao, numero) matches."""
    result = figurinha_repository.find_by_par(codigo_selecao="BRA", numero=1)

    assert result is not None and result.codigo_selecao == "BRA" and result.numero == 1


def test_find_by_par_quando_par_inexistente_deve_retornar_none(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_par must return None when no row matches (codigo_selecao, numero)."""
    result = figurinha_repository.find_by_par(codigo_selecao="ZZZ", numero=99)

    assert result is None


# ===========================================================================
# update_quantidade
# ===========================================================================


def test_update_quantidade_quando_valor_valido_deve_persistir(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """update_quantidade must write the new value to the figurinhas row.

    After calling the method, a direct SELECT confirms the persisted value.
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1")
    assert figurinha is not None

    figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=5)
    db_connection.commit()

    with db_connection.cursor() as cur:
        cur.execute("SELECT quantidade FROM figurinhas WHERE id = %s", (figurinha.id,))
        row = cur.fetchone()

    assert row is not None and row[0] == 5


def test_update_quantidade_deve_atualizar_campo_updated_at(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """update_quantidade must cause the trigger to refresh updated_at.

    The updated_at value after the update must be greater than or equal to
    created_at, confirming the trigger fired.
    """
    figurinha_antes = figurinha_repository.find_by_codigo("BRA-1")
    assert figurinha_antes is not None

    figurinha_repository.update_quantidade(figurinha_id=figurinha_antes.id, quantidade=3)
    db_connection.commit()

    with db_connection.cursor() as cur:
        cur.execute(
            "SELECT updated_at FROM figurinhas WHERE id = %s",
            (figurinha_antes.id,),
        )
        row = cur.fetchone()

    assert row is not None and row[0] >= figurinha_antes.created_at


def test_update_quantidade_quando_quantidade_negativa_deve_rejeitar_constraint(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """update_quantidade with a negative value must trigger the CHECK constraint.

    The database enforces ``quantidade >= 0``; attempting to set a negative
    value must raise a psycopg2 IntegrityError (or DatabaseError).
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1")
    assert figurinha is not None

    with pytest.raises((psycopg2.IntegrityError, psycopg2.DatabaseError)):
        figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=-1)
        db_connection.commit()


# ===========================================================================
# Concorrência básica
# ===========================================================================


def test_dois_updates_sequenciais_devem_resultar_em_valor_final_correto(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Two sequential update_quantidade calls must leave the last value persisted.

    This test verifies that the repository does not cache stale state between
    calls: after updating to 10 and then to 7, the row must contain 7.
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1")
    assert figurinha is not None

    figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=10)
    db_connection.commit()

    figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=7)
    db_connection.commit()

    with db_connection.cursor() as cur:
        cur.execute("SELECT quantidade FROM figurinhas WHERE id = %s", (figurinha.id,))
        row = cur.fetchone()

    assert row is not None and row[0] == 7
