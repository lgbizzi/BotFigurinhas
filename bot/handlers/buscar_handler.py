"""ConversationHandlers for /buscar and /buscar_pais commands.

/buscar  → AGUARDANDO_CODIGO_BUSCA → [end]
/buscar_pais → AGUARDANDO_PAIS_BUSCA → [end]

Each conversation is a single-step exchange: the bot asks for input and
responds with the lookup result.  No domain logic lives in this module.
"""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from controllers.bot_controller import BotController
from views import message_templates as tmpl

logger = logging.getLogger(__name__)

# Conversation state constants
AGUARDANDO_CODIGO_BUSCA: int = 0
AGUARDANDO_PAIS_BUSCA: int = 0


def build_buscar_handlers(controller: BotController) -> list[ConversationHandler]:
    """Construct and return the ConversationHandlers for /buscar and /buscar_pais.

    Args:
        controller: Injected :class:`~controllers.bot_controller.BotController`.

    Returns:
        List with two :class:`telegram.ext.ConversationHandler` instances.
    """

    # ------------------------------------------------------------------
    # /buscar
    # ------------------------------------------------------------------

    async def cmd_buscar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point: ask the user for a sticker code.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            Next conversation state (AGUARDANDO_CODIGO_BUSCA).
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.solicitar_codigo_busca(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return AGUARDANDO_CODIGO_BUSCA

    async def receber_codigo_busca(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Look up the sticker and reply with its stock status.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END.
        """
        entrada = (update.message.text or "").strip()  # type: ignore[union-attr]
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""

        resposta = controller.consultar_buscar(entrada, telegram_user_id, telegram_username)
        await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]
        return ConversationHandler.END

    # ------------------------------------------------------------------
    # /buscar_pais
    # ------------------------------------------------------------------

    async def cmd_buscar_pais(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point: ask the user for a country name.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            Next conversation state (AGUARDANDO_PAIS_BUSCA).
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.solicitar_pais(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return AGUARDANDO_PAIS_BUSCA

    async def receber_pais_busca(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Look up all stickers for the country and reply with the breakdown.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END.
        """
        entrada = (update.message.text or "").strip()  # type: ignore[union-attr]
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""

        resposta = controller.consultar_buscar_pais(entrada, telegram_user_id, telegram_username)
        await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]
        return ConversationHandler.END

    # ------------------------------------------------------------------
    # Shared fallback
    # ------------------------------------------------------------------

    async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the in-progress conversation.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END.
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.operacao_cancelada(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    buscar_handler = ConversationHandler(
        entry_points=[CommandHandler("buscar", cmd_buscar)],
        states={
            AGUARDANDO_CODIGO_BUSCA: [
                CommandHandler("cancelar", cmd_cancelar),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_codigo_busca),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="buscar_conversation",
        persistent=False,
    )

    buscar_pais_handler = ConversationHandler(
        entry_points=[CommandHandler("buscar_pais", cmd_buscar_pais)],
        states={
            AGUARDANDO_PAIS_BUSCA: [
                CommandHandler("cancelar", cmd_cancelar),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_pais_busca),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="buscar_pais_conversation",
        persistent=False,
    )

    return [buscar_handler, buscar_pais_handler]
