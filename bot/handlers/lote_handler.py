"""ConversationHandler for the /adicionar_lote command.

Agent: Bot Interface Dev

Manages a single-state conversation that accepts a multi-line message where
each line is a sticker code.  Each sticker receives +1 quantity.

    /adicionar_lote → AGUARDANDO_LOTE → [end]
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

AGUARDANDO_LOTE: int = 0


def build_lote_handler(controller: BotController) -> ConversationHandler:
    """Construct and return the ConversationHandler for /adicionar_lote.

    Args:
        controller: Injected :class:`~controllers.bot_controller.BotController`.

    Returns:
        A fully configured :class:`telegram.ext.ConversationHandler`.
    """

    async def cmd_adicionar_lote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point: prompt the user to send the list of codes.

        Args:
            update: Incoming Telegram update.
            context: PTB context object (unused).

        Returns:
            Next conversation state (AGUARDANDO_LOTE).
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.solicitar_lote(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return AGUARDANDO_LOTE

    async def receber_lote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process the multi-line sticker list and end the conversation.

        Splits the message text by newline, delegates to the controller, and
        sends the batch result back to the user.

        Args:
            update: Incoming Telegram update carrying the sticker list.
            context: PTB context object (unused).

        Returns:
            ConversationHandler.END.
        """
        texto = (update.message.text or "").strip()  # type: ignore[union-attr]
        entradas = texto.split("\n")

        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""

        resposta = await controller.processar_adicionar_lote(
            entradas_brutas=entradas,
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
        )
        await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]
        return ConversationHandler.END

    async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the in-progress conversation.

        Args:
            update: Incoming Telegram update.
            context: PTB context object (unused).

        Returns:
            ConversationHandler.END.
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.operacao_cancelada(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    return ConversationHandler(
        entry_points=[CommandHandler("adicionar_lote", cmd_adicionar_lote)],
        states={
            AGUARDANDO_LOTE: [
                CommandHandler("cancelar", cmd_cancelar),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_lote),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="lote_conversation",
        persistent=False,
    )
