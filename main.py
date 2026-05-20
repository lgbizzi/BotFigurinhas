"""Application entrypoint for the Album Copa 2026 Telegram bot.

Startup sequence:
1. Load settings (fails fast on missing environment variables).
2. Initialise the PostgreSQL connection pool.
3. Wire dependencies manually (DI by construction).
4. Build the PTB Application and register handlers.
5. Start polling.

Album initialisation is now lazy and per-user: each user's 995 sticker rows
are created on first interaction via
:meth:`~services.figurinha_service.FigurinhaService.garantir_album_inicializado`.
"""

import logging
import sys

# ---------------------------------------------------------------------------
# Logging — configured before any project import so all loggers inherit it
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Settings (fail-fast on missing env vars)
# ---------------------------------------------------------------------------
try:
    import config.settings as settings
except EnvironmentError as exc:
    logger.critical("Configuration error: %s", exc)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Project imports (after settings are validated)
# ---------------------------------------------------------------------------
from psycopg2.extensions import connection as PsycopgConnection
from telegram.ext import Application

from bot.bot_setup import setup_bot
from controllers.bot_controller import BotController
from database.connection import ConnectionPool, ConnectionPoolError
from repositories.figurinha_repository import FigurinhaRepository
from repositories.movimentacao_repository import MovimentacaoRepository
from services.album_query_service import AlbumQueryService
from services.codigo_parser import CodigoParser
from services.figurinha_service import FigurinhaService
from services.movimentacao_service import MovimentacaoService


# ---------------------------------------------------------------------------
# Dependency wiring
# ---------------------------------------------------------------------------


def _build_controller(pool: ConnectionPool) -> tuple[BotController, PsycopgConnection]:
    """Instantiate all layers and return a wired BotController with its connection.

    The caller is responsible for returning the connection to the pool via
    ``pool.release_connection(conn)`` when the controller is no longer needed.

    Args:
        pool: Initialised :class:`~database.connection.ConnectionPool`.

    Returns:
        A tuple of ``(BotController, connection)`` where ``connection`` must be
        released to ``pool`` by the caller.
    """
    conn = pool.get_connection()
    figurinha_repo = FigurinhaRepository(conn)
    movimentacao_repo = MovimentacaoRepository(conn)
    codigo_parser = CodigoParser()
    movimentacao_service = MovimentacaoService(movimentacao_repo)
    figurinha_service = FigurinhaService(figurinha_repo, movimentacao_service, codigo_parser)
    album_query_service = AlbumQueryService(figurinha_repo)
    return BotController(figurinha_service, album_query_service), conn


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the Telegram bot.

    Raises:
        SystemExit: On any fatal initialisation error.
    """
    logger.info("Starting Album Copa 2026 bot.")

    try:
        pool = ConnectionPool.get_instance()
        logger.info("Database connection pool initialised.")
    except ConnectionPoolError as exc:
        logger.critical("Failed to initialise connection pool: %s", exc)
        sys.exit(1)

    controller, conn = _build_controller(pool)
    logger.info("Dependency graph wired successfully.")

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    setup_bot(application, controller)

    logger.info("Bot polling started.")
    try:
        application.run_polling()
    finally:
        pool.release_connection(conn)
        logger.info("Database connection returned to pool.")


if __name__ == "__main__":
    main()
