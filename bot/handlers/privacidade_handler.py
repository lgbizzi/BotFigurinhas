"""Handlers for /consulta and /excluir_usuario commands.

/consulta  → returns a summary of data stored for the user (no conversation).
/excluir_usuario → AGUARDANDO_CONFIRMACAO_EXCLUSAO → [end]

The deletion flow requires explicit "Sim" confirmation before proceeding.
Any other response (including "Não") cancels the operation.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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

AGUARDANDO_CONFIRMACAO_EXCLUSAO: int = 0

_SIM = "Sim"
_NAO = "Não"
_TECLADO = ReplyKeyboardMarkup([[_SIM, _NAO]], one_time_keyboard=True, resize_keyboard=True)


def build_privacidade_handlers(controller: BotController) -> list:
    """Construct and return handlers for /consulta and /excluir_usuario.

    Args:
        controller: Injected :class:`~controllers.bot_controller.BotController`.

    Returns:
        List with a plain CommandHandler for /consulta and a
        ConversationHandler for /excluir_usuario.
    """

    # ------------------------------------------------------------------
    # /consulta — single-shot command, no conversation needed
    # ------------------------------------------------------------------

    async def cmd_consulta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /consulta: reply with data stored for the user.

        Args:
            update: Incoming Telegram update.
            context: PTB context object (unused).
        """
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""

        resposta = controller.consultar_dados_usuario(telegram_user_id, telegram_username)
        await update.message.reply_text(  # type: ignore[union-attr]
            resposta,
            parse_mode=ParseMode.MARKDOWN,
        )

    # ------------------------------------------------------------------
    # /excluir_usuario — two-step conversation with explicit confirmation
    # ------------------------------------------------------------------

    async def cmd_excluir_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point: show the irreversibility warning and ask for confirmation.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            Next conversation state (AGUARDANDO_CONFIRMACAO_EXCLUSAO).
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.confirmacao_exclusao(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_TECLADO,
        )
        return AGUARDANDO_CONFIRMACAO_EXCLUSAO

    async def receber_confirmacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process the user's confirmation reply.

        Deletes all user data on "Sim"; cancels silently on any other input.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END.
        """
        resposta_usuario = (update.message.text or "").strip()  # type: ignore[union-attr]
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""
        remove_teclado = ReplyKeyboardRemove()

        if resposta_usuario.lower() in ("sim", "s", "yes"):
            mensagem = controller.excluir_usuario(telegram_user_id, telegram_username)
        else:
            mensagem = tmpl.cancelar_exclusao()

        await update.message.reply_text(  # type: ignore[union-attr]
            mensagem,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=remove_teclado,
        )
        return ConversationHandler.END

    async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the deletion flow via /cancelar command.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END.
        """
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.cancelar_exclusao(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    excluir_handler = ConversationHandler(
        entry_points=[CommandHandler("excluir_usuario", cmd_excluir_usuario)],
        states={
            AGUARDANDO_CONFIRMACAO_EXCLUSAO: [
                CommandHandler("cancelar", cmd_cancelar),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_confirmacao),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="excluir_usuario_conversation",
        persistent=False,
    )

    return [CommandHandler("consulta", cmd_consulta), excluir_handler]
