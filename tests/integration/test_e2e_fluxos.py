"""Integration E2E tests for the /adicionar, /remover and /progresso flows.

Agent: Tests Analyst

These tests exercise the full stack from :class:`~controllers.bot_controller.BotController`
through :class:`~services.figurinha_service.FigurinhaService` down to the real
PostgreSQL database.  No mocks are used — every layer is wired with concrete
implementations against the session-scoped test database.

Isolation strategy:
    Each test uses a distinct ``telegram_user_id`` (range 11–16).  Because the
    service layer calls ``conn.commit()`` internally, ``SAVEPOINT``-based rollback
    is ineffective for reverting E2E writes.  True isolation is provided by (a) the
    unique-user-id strategy (no two tests share a user) and (b) a session-scoped
    teardown fixture that deletes all rows for user IDs 11–16 after the test
    session ends.

Test naming convention:
    ``test_<flow>_<condition>_deve_<expected>``

Structure:
    - Arrange / Act / Assert blocks separated by blank lines.
    - One logical assertion cluster per test function.
    - Zero business logic inside tests (no ``if``, ``for``, computed values).
    - Each test is independently executable; no inter-test state dependencies.
"""

import asyncio

import psycopg2.extensions
import pytest

from controllers.bot_controller import BotController
from repositories.figurinha_repository import FigurinhaRepository
from repositories.movimentacao_repository import MovimentacaoRepository
from services.album_query_service import AlbumQueryService
from services.codigo_parser import CodigoParser
from services.figurinha_service import FigurinhaService
from services.movimentacao_service import MovimentacaoService

# ---------------------------------------------------------------------------
# Telegram user IDs — one per test to ensure full isolation.
# Must NOT overlap with the seed user (0) or any fixture user (123456789).
# ---------------------------------------------------------------------------
_USER_ADICIONAR_INCREMENTA = 11
_USER_ADICIONAR_CODIGO_INVALIDO = 12
_USER_ADICIONAR_QUANTIDADE_INVALIDA = 13
_USER_REMOVER_DECREMENTA = 14
_USER_REMOVER_SALDO_INSUFICIENTE = 15
_USER_PROGRESSO = 16
_USERNAME = "e2e_test_user"
_E2E_USER_IDS = (11, 12, 13, 14, 15, 16)


# ---------------------------------------------------------------------------
# Teardown: remove E2E rows after the session (commits bypass savepoints)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def cleanup_e2e_users(db_connection: psycopg2.extensions.connection):
    """Delete all figurinha and movimentacao rows for E2E test users after the session.

    Args:
        db_connection: Session-scoped open connection from conftest.

    Yields:
        Nothing — cleanup happens on teardown.
    """
    yield
    placeholders = ", ".join(["%s"] * len(_E2E_USER_IDS))
    with db_connection.cursor() as cur:
        cur.execute(
            f"DELETE FROM movimentacoes WHERE telegram_user_id IN ({placeholders})",
            _E2E_USER_IDS,
        )
        cur.execute(
            f"DELETE FROM figurinhas WHERE telegram_user_id IN ({placeholders})",
            _E2E_USER_IDS,
        )
    db_connection.commit()


# ---------------------------------------------------------------------------
# Helper: build a fully-wired BotController against the test database
# ---------------------------------------------------------------------------


def _build_controller(connection: psycopg2.extensions.connection) -> BotController:
    """Instantiate a :class:`BotController` with all real collaborators.

    Args:
        connection: Open psycopg2 connection to the test database.

    Returns:
        A :class:`BotController` ready for E2E testing.
    """
    figurinha_repo = FigurinhaRepository(connection=connection)
    movimentacao_repo = MovimentacaoRepository(connection=connection)
    codigo_parser = CodigoParser()
    movimentacao_service = MovimentacaoService(movimentacao_repository=movimentacao_repo)
    figurinha_service = FigurinhaService(
        figurinha_repository=figurinha_repo,
        movimentacao_service=movimentacao_service,
        codigo_parser=codigo_parser,
    )
    album_query_service = AlbumQueryService(figurinha_repository=figurinha_repo)
    return BotController(
        figurinha_service=figurinha_service,
        album_query_service=album_query_service,
    )


# ===========================================================================
# Fluxo /adicionar
# ===========================================================================


def test_adicionar_figurinha_existente_incrementa_quantidade(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Adicionar 2 figurinhas de BRA-1 deve retornar figurinha com saldo 2.

    The user album is initialized on the first call (all 994 stickers with
    quantidade=0).  After adding 2 copies of BRA-1 the confirmation message
    must report the updated balance of 2.
    """
    controller = _build_controller(db_connection)

    result = asyncio.run(
        controller.processar_adicionar(
            entrada_bruta="BRA-1",
            quantidade=2,
            telegram_user_id=_USER_ADICIONAR_INCREMENTA,
            telegram_username=_USERNAME,
        )
    )

    assert "Saldo atual: *2*" in result


def test_adicionar_figurinha_codigo_invalido_retorna_erro(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Adicionar uma figurinha com código inexistente deve retornar mensagem de erro.

    The raw input ``"XXX-99"`` cannot be resolved to any album sticker.
    The controller must return a user-friendly error string containing the
    invalid-code marker, never raising an exception to the caller.
    """
    controller = _build_controller(db_connection)

    result = asyncio.run(
        controller.processar_adicionar(
            entrada_bruta="XXX-99",
            quantidade=1,
            telegram_user_id=_USER_ADICIONAR_CODIGO_INVALIDO,
            telegram_username=_USERNAME,
        )
    )

    assert "❌" in result
    assert "XXX-99" in result


def test_adicionar_figurinha_quantidade_invalida_retorna_erro(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Adicionar uma figurinha com quantidade 0 deve retornar mensagem de erro.

    A quantidade of 0 violates the domain rule (must be >= 1).  The controller
    must return an error string without propagating ValueError to the caller.
    The message must contain the generic error marker and not a success marker.
    """
    controller = _build_controller(db_connection)

    result = asyncio.run(
        controller.processar_adicionar(
            entrada_bruta="BRA-1",
            quantidade=0,
            telegram_user_id=_USER_ADICIONAR_QUANTIDADE_INVALIDA,
            telegram_username=_USERNAME,
        )
    )

    assert "❌" in result
    assert "✅" not in result


# ===========================================================================
# Fluxo /remover
# ===========================================================================


def test_remover_figurinha_com_saldo_decrementa_quantidade(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Adicionar 3 e depois remover 2 de BRA-1 deve resultar em saldo 1.

    Two sequential controller calls simulate a real user session: first the
    sticker is added three times, then two are removed.  The removal
    confirmation message must report the final balance of 1.
    """
    controller = _build_controller(db_connection)
    asyncio.run(
        controller.processar_adicionar(
            entrada_bruta="BRA-1",
            quantidade=3,
            telegram_user_id=_USER_REMOVER_DECREMENTA,
            telegram_username=_USERNAME,
        )
    )

    result = asyncio.run(
        controller.processar_remover(
            entrada_bruta="BRA-1",
            quantidade=2,
            telegram_user_id=_USER_REMOVER_DECREMENTA,
            telegram_username=_USERNAME,
        )
    )

    assert "Saldo atual: *1*" in result


def _inicializar_album_via_adicionar(
    controller: BotController,
    telegram_user_id: int,
) -> None:
    """Trigger album initialization by adding one sticker.

    Args:
        controller: Wired :class:`BotController` instance.
        telegram_user_id: User whose album should be initialized.
    """
    asyncio.run(
        controller.processar_adicionar(
            entrada_bruta="BRA-1",
            quantidade=1,
            telegram_user_id=telegram_user_id,
            telegram_username=_USERNAME,
        )
    )


def test_remover_mais_do_que_disponivel_retorna_erro(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Tentar remover mais figurinhas do que o saldo disponível deve retornar erro.

    After initialization BRA-1 has quantidade=1.  Attempting to remove 5 copies
    must trigger ``QuantidadeInsuficienteError`` inside the service, which the
    controller catches and converts to an error string containing both the error
    marker and the sticker code.
    """
    controller = _build_controller(db_connection)
    _inicializar_album_via_adicionar(controller, _USER_REMOVER_SALDO_INSUFICIENTE)

    result = asyncio.run(
        controller.processar_remover(
            entrada_bruta="BRA-1",
            quantidade=5,
            telegram_user_id=_USER_REMOVER_SALDO_INSUFICIENTE,
            telegram_username=_USERNAME,
        )
    )

    assert "❌" in result
    assert "BRA-1" in result


# ===========================================================================
# Fluxo /progresso
# ===========================================================================


def test_progresso_retorna_percentual_e_contagens(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Após inicializar o álbum, o progresso deve exibir 0.0% e 994 faltantes.

    The user's album is implicitly initialized by the first ``consultar_progresso``
    call (via ``garantir_album_inicializado``).  With all 994 sticker types at
    quantidade=0 the formatted message must report 0.0% completion and 994 types
    still missing.

    ``Progresso.percentual`` is typed as ``float`` and returns ``0.0`` for a
    brand-new album, so the template produces the literal string ``"0.0% completo"``.
    """
    controller = _build_controller(db_connection)

    result = controller.consultar_progresso(
        telegram_user_id=_USER_PROGRESSO,
        telegram_username=_USERNAME,
    )

    assert "0.0% completo" in result
    assert "994" in result
