"""Command handlers for /progresso, /faltantes, and /repetidas.

Agent: Bot Interface Dev

Each handler calls the corresponding :class:`~controllers.bot_controller.BotController`
method and replies to the user.  Long messages (> 4 096 chars) are split at
newline boundaries and sent as separate messages.

No business logic lives here — all domain work is done inside the controller.
"""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from controllers.bot_controller import BotController

logger = logging.getLogger(__name__)

_MAX_MESSAGE_LEN: int = 4096


def _split_message(text: str, max_len: int = _MAX_MESSAGE_LEN) -> list[str]:
    """Split a long message into chunks that respect newline boundaries.

    Args:
        text: Full message text to split.
        max_len: Maximum allowed length per chunk (default: 4 096).

    Returns:
        List of string chunks each no longer than ``max_len`` characters.
    """
    if len(text) <= max_len:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for line in text.split("\n"):
        line_len = len(line) + 1  # +1 for the newline
        if current_len + line_len > max_len and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current))

    return chunks


def build_consultas_handlers(controller: BotController) -> list[CommandHandler]:
    """Construct and return all three read-only command handlers.

    Args:
        controller: Injected :class:`~controllers.bot_controller.BotController`.

    Returns:
        List containing CommandHandlers for ``/progresso``, ``/faltantes``,
        and ``/repetidas``.
    """

    async def cmd_progresso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /progresso command.

        Args:
            update: Incoming Telegram update.
            context: PTB context object (unused).
        """
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""
        result = controller.consultar_progresso(telegram_user_id, telegram_username)
        for chunk in _split_message(result):
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]

    async def cmd_faltantes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /faltantes command.

        The controller returns one message string per album group.  Each
        string is split further (if needed) to respect the Telegram
        4 096-character limit, and every resulting chunk is sent as an
        individual reply.

        Args:
            update: Incoming Telegram update.
            context: PTB context object (unused).
        """
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""
        mensagens = controller.consultar_faltantes(telegram_user_id, telegram_username)
        for msg in mensagens:
            for chunk in _split_message(msg):
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]

    async def cmd_repetidas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /repetidas command.

        Args:
            update: Incoming Telegram update.
            context: PTB context object (unused).
        """
        user = update.effective_user
        telegram_user_id: int = user.id if user else 0
        telegram_username: str = (user.username or "") if user else ""
        mensagens = controller.consultar_repetidas(telegram_user_id, telegram_username)
        for msg in mensagens:
            for chunk in _split_message(msg):
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)  # type: ignore[union-attr]

    return [
        CommandHandler("progresso", cmd_progresso),
        CommandHandler("faltantes", cmd_faltantes),
        CommandHandler("repetidas", cmd_repetidas),
    ]
