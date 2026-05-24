"""Bot registration: wires all handlers into a PTB Application instance.

Call :func:`setup_bot` once during application startup, after the
:class:`~telegram.ext.Application` object has been created but before
``run_polling()`` is invoked.
"""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.handlers.adicionar_handler import build_adicionar_handler
from bot.handlers.buscar_handler import build_buscar_handlers
from bot.handlers.privacidade_handler import build_privacidade_handlers
from bot.handlers.consultas_handler import build_consultas_handlers
from bot.handlers.lote_handler import build_lote_handler
from bot.handlers.remover_handler import build_remover_handler
from controllers.bot_controller import BotController
from views import message_templates as tmpl

logger = logging.getLogger(__name__)


async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command by sending the welcome message.

    Args:
        update: Incoming Telegram update.
        context: PTB context object (unused).
    """
    await update.message.reply_text(  # type: ignore[union-attr]
        tmpl.boas_vindas(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log unexpected errors and, where possible, notify the user.

    Args:
        update: The update that triggered the error (may not be a full Update).
        context: PTB context carrying the raised exception.
    """
    logger.exception("Unhandled exception in PTB dispatcher: %s", context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            tmpl.erro_generico(),
            parse_mode=ParseMode.MARKDOWN,
        )


def setup_bot(application: Application, bot_controller: BotController) -> None:
    """Register all ConversationHandlers and commands on the Application.

    Adds:
    - ``/start`` command handler
    - ``/adicionar`` ConversationHandler
    - ``/remover`` ConversationHandler
    - Global error handler

    Args:
        application: PTB :class:`~telegram.ext.Application` instance to configure.
        bot_controller: Injected :class:`~controllers.bot_controller.BotController`.
    """
    application.add_handler(CommandHandler("start", _cmd_start))
    application.add_handler(build_adicionar_handler(bot_controller))
    application.add_handler(build_remover_handler(bot_controller))
    application.add_handler(build_lote_handler(bot_controller))
    for handler in build_consultas_handlers(bot_controller):
        application.add_handler(handler)
    for handler in build_buscar_handlers(bot_controller):
        application.add_handler(handler)
    for handler in build_privacidade_handlers(bot_controller):
        application.add_handler(handler)
    application.add_error_handler(_error_handler)

    logger.info("Bot handlers registered successfully.")
