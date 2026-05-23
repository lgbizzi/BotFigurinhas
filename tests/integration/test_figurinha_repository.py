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

    BRA-1 is guaranteed to exist because it is inserted as the session seed
    for telegram_user_id=0.
    """
    result = figurinha_repository.find_by_codigo("BRA-1", 0)

    assert isinstance(result, Figurinha)


def test_find_by_codigo_quando_codigo_existe_deve_retornar_codigo_correto(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_codigo must return the Figurinha whose codigo_figurinha matches."""
    result = figurinha_repository.find_by_codigo("BRA-1", 0)

    assert result is not None and result.codigo_figurinha == "BRA-1"


def test_find_by_codigo_quando_codigo_inexistente_deve_retornar_none(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_codigo must return None for a code that has no row in the DB."""
    result = figurinha_repository.find_by_codigo("ZZZ-99", 0)

    assert result is None


# ===========================================================================
# find_by_par (codigo_selecao, numero)
# ===========================================================================


def test_find_by_par_quando_par_existe_deve_retornar_figurinha(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_par must return a Figurinha when (codigo_selecao, numero) matches.

    The seed row for telegram_user_id=0 has codigo_selecao='BRA' and numero=1.
    """
    result = figurinha_repository.find_by_par(codigo_selecao="BRA", numero=1, telegram_user_id=0)

    assert isinstance(result, Figurinha)


def test_find_by_par_quando_par_existe_deve_retornar_par_correto(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_par must return the Figurinha whose (codigo_selecao, numero) matches."""
    result = figurinha_repository.find_by_par(codigo_selecao="BRA", numero=1, telegram_user_id=0)

    assert result is not None and result.codigo_selecao == "BRA" and result.numero == 1


def test_find_by_par_quando_par_inexistente_deve_retornar_none(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """find_by_par must return None when no row matches (codigo_selecao, numero)."""
    result = figurinha_repository.find_by_par(codigo_selecao="ZZZ", numero=99, telegram_user_id=0)

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
    The seed row for telegram_user_id=0 is used as the known-present figurinha.
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1", 0)
    assert figurinha is not None

    figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=5, telegram_user_id=0)
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
    The seed row for telegram_user_id=0 is used as the known-present figurinha.
    """
    figurinha_antes = figurinha_repository.find_by_codigo("BRA-1", 0)
    assert figurinha_antes is not None

    figurinha_repository.update_quantidade(figurinha_id=figurinha_antes.id, quantidade=3, telegram_user_id=0)
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
    The seed row for telegram_user_id=0 is used as the known-present figurinha.
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1", 0)
    assert figurinha is not None

    with pytest.raises((psycopg2.IntegrityError, psycopg2.DatabaseError)):
        figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=-1, telegram_user_id=0)
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
    The seed row for telegram_user_id=0 is used as the known-present figurinha.
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1", 0)
    assert figurinha is not None

    figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=10, telegram_user_id=0)
    db_connection.commit()

    figurinha_repository.update_quantidade(figurinha_id=figurinha.id, quantidade=7, telegram_user_id=0)
    db_connection.commit()

    with db_connection.cursor() as cur:
        cur.execute("SELECT quantidade FROM figurinhas WHERE id = %s", (figurinha.id,))
        row = cur.fetchone()

    assert row is not None and row[0] == 7


# ===========================================================================
# find_faltantes — ordenação por pagina
# ===========================================================================


def test_find_faltantes_deve_ordenar_resultados_por_pagina_e_numero(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """find_faltantes must return stickers ordered by pagina ascending.

    MEX is on page 8 and BRA is on page 24; MEX-1 must appear before BRA-1
    when both have quantidade=0.
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'A', 'MEX', 'México', 1, 'MEX-1', 0, 8) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
            (telegram_user_id,),
        )
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'C', 'BRA', 'Brasil', 1, 'BRA-1', 0, 24) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
            (telegram_user_id,),
        )

    faltantes = figurinha_repository.find_faltantes(telegram_user_id)

    assert faltantes[0].codigo_figurinha == "MEX-1"


def test_find_faltantes_deve_ordenar_mex_antes_de_bra_por_pagina(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """find_faltantes must place MEX-1 (page 8) strictly before BRA-1 (page 24)."""
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'A', 'MEX', 'México', 1, 'MEX-1', 0, 8) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
            (telegram_user_id,),
        )
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'C', 'BRA', 'Brasil', 1, 'BRA-1', 0, 24) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
            (telegram_user_id,),
        )

    faltantes = figurinha_repository.find_faltantes(telegram_user_id)

    assert faltantes[-1].codigo_figurinha == "BRA-1"


# ===========================================================================
# find_repetidas — ordenação por pagina
# ===========================================================================


def test_find_repetidas_deve_ordenar_resultados_por_pagina_e_numero(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """find_repetidas must return stickers ordered by pagina ascending.

    MEX is on page 8 and BRA is on page 24; MEX-1 (quantidade=3) must appear
    before BRA-1 (quantidade=2) in the result list.
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'A', 'MEX', 'México', 1, 'MEX-1', 3, 8) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO UPDATE SET quantidade = 3",
            (telegram_user_id,),
        )
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'C', 'BRA', 'Brasil', 1, 'BRA-1', 2, 24) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO UPDATE SET quantidade = 2",
            (telegram_user_id,),
        )

    repetidas = figurinha_repository.find_repetidas(telegram_user_id)

    assert repetidas[0].codigo_figurinha == "MEX-1"


def test_find_repetidas_deve_colocar_bra_depois_de_mex_por_pagina(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """find_repetidas must place BRA-1 (page 24) after MEX-1 (page 8)."""
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'A', 'MEX', 'México', 1, 'MEX-1', 3, 8) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO UPDATE SET quantidade = 3",
            (telegram_user_id,),
        )
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'C', 'BRA', 'Brasil', 1, 'BRA-1', 2, 24) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO UPDATE SET quantidade = 2",
            (telegram_user_id,),
        )

    repetidas = figurinha_repository.find_repetidas(telegram_user_id)

    assert repetidas[-1].codigo_figurinha == "BRA-1"


# ===========================================================================
# FWC-20 ausência no banco
# ===========================================================================


def test_fwc20_nao_deve_existir_no_banco(
    figurinha_repository: FigurinhaRepository,
    user_info: dict,
) -> None:
    """FWC-20 does not exist in the real album; find_by_codigo must return None.

    The album runs FWC-0 to FWC-19 (20 stickers total). FWC-20 was removed
    from scope on 2026-05-23 — the database must never contain this code.
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    result = figurinha_repository.find_by_codigo("FWC-20", telegram_user_id)

    assert result is None


# ===========================================================================
# Campo pagina na model retornada
# ===========================================================================


def test_figurinha_deve_ter_campo_pagina(
    figurinha_repository: FigurinhaRepository,
) -> None:
    """Figurinha returned by find_by_codigo must expose the pagina attribute.

    BRA-1 is the seed row (telegram_user_id=0); its pagina value must be 24
    (BRA section page in the album).
    """
    figurinha = figurinha_repository.find_by_codigo("BRA-1", 0)

    assert figurinha is not None and figurinha.pagina == 24

# ===========================================================================
# get_selecoes_faltantes_contagem
# ===========================================================================


def test_get_selecoes_faltantes_contagem_deve_ordenar_por_faltantes_ascendente(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """get_selecoes_faltantes_contagem must return all selections ordered ASC by faltantes.

    Two countries are inserted: 'Q01' with 1 missing sticker (smaller) and
    'Q02' with 5 missing stickers.  The first entry must belong to 'Q01'.
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        for numero in range(1, 21):
            quantidade_q01 = 0 if numero == 1 else 1
            cur.execute(
                "INSERT INTO figurinhas "
                "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
                "codigo_figurinha, quantidade, pagina) "
                "VALUES (%s, 'G', 'Q01', 'Quase01', %s, %s, %s, 75) "
                "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
                (telegram_user_id, numero, f"Q01-{numero}", quantidade_q01),
            )
        for numero in range(1, 21):
            quantidade_q02 = 0 if numero <= 5 else 1
            cur.execute(
                "INSERT INTO figurinhas "
                "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
                "codigo_figurinha, quantidade, pagina) "
                "VALUES (%s, 'G', 'Q02', 'Quase02', %s, %s, %s, 76) "
                "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
                (telegram_user_id, numero, f"Q02-{numero}", quantidade_q02),
            )

    result = figurinha_repository.get_selecoes_faltantes_contagem(telegram_user_id)

    assert result[0][0] == "Quase01"


def test_get_selecoes_faltantes_contagem_deve_retornar_todas_selecoes(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """get_selecoes_faltantes_contagem must return all selections, not just top-3.

    Four countries are inserted, each with different faltantes counts.  The
    returned list must include all four — limiting to top-3 is the caller's
    responsibility.
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        for selecao_idx, qtd_faltantes in enumerate([1, 2, 3, 4], start=1):
            codigo = f"T{selecao_idx:02d}"
            for numero in range(1, 21):
                quantidade = 0 if numero <= qtd_faltantes else 1
                cur.execute(
                    "INSERT INTO figurinhas "
                    "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
                    "codigo_figurinha, quantidade, pagina) "
                    "VALUES (%s, 'K', %s, %s, %s, %s, %s, 90) "
                    "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
                    (telegram_user_id, codigo, f"Total{selecao_idx:02d}", numero,
                     f"{codigo}-{numero}", quantidade),
                )

    result = figurinha_repository.get_selecoes_faltantes_contagem(telegram_user_id)

    assert len(result) >= 4


# ===========================================================================
# get_cc_faltantes
# ===========================================================================


def test_get_cc_faltantes_deve_retornar_cc_com_quantidade_zero(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """get_cc_faltantes must include CC stickers with quantidade=0.

    A CC figurinha with quantidade=0 is inserted.  Its codigo_figurinha must
    appear in the returned list.
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'CC', 'CC', 'Campeonatos Continentais', 7, 'CC-7', 0, 5) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING",
            (telegram_user_id,),
        )

    result = figurinha_repository.get_cc_faltantes(telegram_user_id)

    assert "CC-7" in result


def test_get_cc_faltantes_nao_deve_incluir_cc_com_quantidade_positiva(
    figurinha_repository: FigurinhaRepository,
    db_connection: psycopg2.extensions.connection,
    user_info: dict,
) -> None:
    """get_cc_faltantes must not include CC stickers already owned (quantidade > 0).

    A CC figurinha with quantidade=1 is inserted.  The returned list must be
    empty (assuming no other CC stickers exist for this user).
    """
    telegram_user_id: int = user_info["telegram_user_id"]  # type: ignore[assignment]

    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, "
            "codigo_figurinha, quantidade, pagina) "
            "VALUES (%s, 'CC', 'CC', 'Campeonatos Continentais', 3, 'CC-3', 1, 5) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO UPDATE SET quantidade = 1",
            (telegram_user_id,),
        )

    result = figurinha_repository.get_cc_faltantes(telegram_user_id)

    assert "CC-3" not in result
