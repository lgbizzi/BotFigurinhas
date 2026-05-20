"""ConversationHandler for the /adicionar command.

Manages a two-state conversation:

    /adicionar → AGUARDANDO_CODIGO → AGUARDANDO_QUANTIDADE → [end]

All business validation is delegated to :class:`~controllers.bot_controller.BotController`.
No domain logic lives in this module.
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
AGUARDANDO_CODIGO: int = 0
AGUARDANDO_QUANTIDADE: int = 1

# user_data keys
_KEY_CODIGO: str = "adicionar_codigo"
_KEY_FIGURINHA: str = "adicionar_figurinha"


def _limpar_user_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove keys stored by this handler from context.user_data.

    Args:
        context: PTB context object carrying user_data.
    """
    context.user_data.pop(_KEY_CODIGO, None)  # type: ignore[union-attr]
    context.user_data.pop(_KEY_FIGURINHA, None)  # type: ignore[union-attr]


def build_adicionar_handler(controller: BotController) -> ConversationHandler:
    """Construct and return the ConversationHandler for /adicionar.

    Args:
        controller: Injected :class:`~controllers.bot_controller.BotController`.

    Returns:
        A fully configured :class:`telegram.ext.ConversationHandler`.
    """

    async def cmd_adicionar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point: send the code-request prompt and enter AGUARDANDO_CODIGO.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            Next conversation state (AGUARDANDO_CODIGO).
        """
        _limpar_user_data(context)
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.solicitar_codigo(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return AGUARDANDO_CODIGO

    async def receber_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Validate the user-supplied code and advance or stay in current state.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            AGUARDANDO_QUANTIDADE on success, AGUARDANDO_CODIGO on failure.
        """
        entrada = (update.message.text or "").strip()  # type: ignore[union-attr]
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""
        figurinha, erro = controller.resolver_codigo(entrada, telegram_user_id, telegram_username)

        if erro is not None:
            await update.message.reply_text(erro, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]
            return AGUARDANDO_CODIGO

        context.user_data[_KEY_CODIGO] = figurinha.codigo_figurinha  # type: ignore[index]
        context.user_data[_KEY_FIGURINHA] = figurinha  # type: ignore[index]
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.solicitar_quantidade_adicionar(
                nome_selecao=figurinha.nome_selecao,
                codigo=figurinha.codigo_figurinha,
                saldo_atual=figurinha.quantidade,
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
        return AGUARDANDO_QUANTIDADE

    async def receber_quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process the quantity, call the controller, and end the conversation.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END on success, AGUARDANDO_QUANTIDADE on failure.
        """
        texto = (update.message.text or "").strip()  # type: ignore[union-attr]
        if not texto.isdigit() or int(texto) < 1:
            await update.message.reply_text(  # type: ignore[union-attr]
                tmpl.erro_quantidade_invalida(),
                parse_mode=ParseMode.MARKDOWN,
            )
            return AGUARDANDO_QUANTIDADE

        quantidade = int(texto)
        codigo = context.user_data.get(_KEY_CODIGO, "")  # type: ignore[union-attr]
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = user.username or "" if user else ""

        resposta = await controller.processar_adicionar(
            entrada_bruta=codigo,
            quantidade=quantidade,
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
        )
        _limpar_user_data(context)
        await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]
        return ConversationHandler.END

    async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the in-progress conversation at any state.

        Args:
            update: Incoming Telegram update.
            context: PTB context object.

        Returns:
            ConversationHandler.END.
        """
        _limpar_user_data(context)
        await update.message.reply_text(  # type: ignore[union-attr]
            tmpl.operacao_cancelada(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    return ConversationHandler(
        entry_points=[CommandHandler("adicionar", cmd_adicionar)],
        states={
            AGUARDANDO_CODIGO: [
                CommandHandler("cancelar", cmd_cancelar),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_codigo),
            ],
            AGUARDANDO_QUANTIDADE: [
                CommandHandler("cancelar", cmd_cancelar),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_quantidade),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="adicionar_conversation",
        persistent=False,
    )
