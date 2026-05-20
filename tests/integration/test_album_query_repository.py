"""Integration tests for FigurinhaRepository — new query methods (TDD RED phase).

Agent: Tests Analyst

These tests run against a real PostgreSQL database (the test database created
by the session-scoped ``db_connection`` fixture in ``conftest.py``).  No mocks
are used for the database layer.

The test DB is seeded with a single row: BRA-1 with ``quantidade=0``.

Methods under test (not yet implemented — RED phase):
    - FigurinhaRepository.find_faltantes()
    - FigurinhaRepository.find_repetidas()
    - FigurinhaRepository.get_progresso()

Test naming convention:
    test_<method>_<condition>_deve_<expected_result>

Structure:
    - Arrange / Act / Assert blocks separated by blank lines.
    - One assertion per test function where possible.
    - Zero business logic inside tests.

Isolation:
    Every test is wrapped in the ``db_transaction`` fixture (declared via
    ``pytestmark``) which rolls back to a savepoint after each test.
"""

import pytest
import psycopg2.extensions

from models.figurinha import Figurinha
from repositories.figurinha_repository import FigurinhaRepository

# Apply savepoint-based rollback to every test in this module.
pytestmark = pytest.mark.usefixtures("db_transaction")


# ===========================================================================
# find_faltantes
# ===========================================================================


def test_find_faltantes_quando_quantidade_zero_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """BRA-1 (qty=0) must appear in find_faltantes results.

    The seed row has quantidade=0 so it must be included in the missing list.
    """
    result = figurinha_repository.find_faltantes()

    codigos = [f.codigo_figurinha for f in result]
    assert "BRA-1" in codigos


def test_find_faltantes_retorna_instancias_de_figurinha(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """All items returned by find_faltantes must be Figurinha instances."""
    result = figurinha_repository.find_faltantes()

    assert all(isinstance(f, Figurinha) for f in result)


def test_find_faltantes_quando_quantidade_positiva_nao_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """After updating BRA-1 to qty=1, it must NOT appear in find_faltantes.

    A sticker with quantity > 0 is no longer missing.
    """
    with db_connection.cursor() as cur:
        cur.execute(
            "UPDATE figurinhas SET quantidade = 1 WHERE codigo_figurinha = 'BRA-1'"
        )
    db_connection.commit()

    result = figurinha_repository.find_faltantes()

    codigos = [f.codigo_figurinha for f in result]
    assert "BRA-1" not in codigos


# ===========================================================================
# find_repetidas
# ===========================================================================


def test_find_repetidas_quando_quantidade_maior_que_um_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """After updating BRA-1 to qty=2, it must appear in find_repetidas.

    A sticker is "repeated" when quantidade > 1.
    """
    with db_connection.cursor() as cur:
        cur.execute(
            "UPDATE figurinhas SET quantidade = 2 WHERE codigo_figurinha = 'BRA-1'"
        )
    db_connection.commit()

    result = figurinha_repository.find_repetidas()

    codigos = [f.codigo_figurinha for f in result]
    assert "BRA-1" in codigos


def test_find_repetidas_quando_quantidade_um_nao_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """After updating BRA-1 to qty=1, it must NOT appear in find_repetidas.

    Owning exactly one copy of a sticker means it is not repeated.
    """
    with db_connection.cursor() as cur:
        cur.execute(
            "UPDATE figurinhas SET quantidade = 1 WHERE codigo_figurinha = 'BRA-1'"
        )
    db_connection.commit()

    result = figurinha_repository.find_repetidas()

    codigos = [f.codigo_figurinha for f in result]
    assert "BRA-1" not in codigos


def test_find_repetidas_retorna_instancias_de_figurinha(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """All items returned by find_repetidas must be Figurinha instances."""
    with db_connection.cursor() as cur:
        cur.execute(
            "UPDATE figurinhas SET quantidade = 3 WHERE codigo_figurinha = 'BRA-1'"
        )
    db_connection.commit()

    result = figurinha_repository.find_repetidas()

    assert all(isinstance(f, Figurinha) for f in result)


# ===========================================================================
# get_progresso
# ===========================================================================


def test_get_progresso_deve_retornar_contagens_corretas(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """With BRA-1 at qty=0: tipos_possuidos=0, total_exemplares=0, total_album=1."""
    result = figurinha_repository.get_progresso()

    assert result.tipos_possuidos == 0


def test_get_progresso_total_album_deve_ser_um(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """The test DB contains exactly one row so total_album must equal 1."""
    result = figurinha_repository.get_progresso()

    assert result.total_album == 1


def test_get_progresso_total_exemplares_com_quantidade_zero_deve_ser_zero(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """With BRA-1 at qty=0: SUM(quantidade) must equal 0."""
    result = figurinha_repository.get_progresso()

    assert result.total_exemplares == 0


def test_get_progresso_apos_atualizar_deve_contar_corretamente(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """After updating BRA-1 to qty=3: tipos_possuidos=1, total_exemplares=3."""
    with db_connection.cursor() as cur:
        cur.execute(
            "UPDATE figurinhas SET quantidade = 3 WHERE codigo_figurinha = 'BRA-1'"
        )
    db_connection.commit()

    result = figurinha_repository.get_progresso()

    assert result.tipos_possuidos == 1


def test_get_progresso_apos_atualizar_total_exemplares_deve_ser_tres(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
) -> None:
    """After updating BRA-1 to qty=3: total_exemplares must equal 3."""
    with db_connection.cursor() as cur:
        cur.execute(
            "UPDATE figurinhas SET quantidade = 3 WHERE codigo_figurinha = 'BRA-1'"
        )
    db_connection.commit()

    result = figurinha_repository.get_progresso()

    assert result.total_exemplares == 3
