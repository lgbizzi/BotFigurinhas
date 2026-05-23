"""Smoke test — verifica se o bot consegue enviar uma mensagem ao usuário real.

Este teste faz uma chamada real à API do Telegram usando o token do bot
definido em .env. Não usa mocks nem banco de dados.

Uso:
    pytest tests/test_telegram_send_message.py -v
"""

import asyncio

import pytest
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

import config.settings as settings

TARGET_USER_ID = 510539283


@pytest.mark.asyncio
async def test_bot_sends_message_to_user():
    """Bot deve conseguir enviar uma mensagem de teste ao usuário LGBizzi."""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async with bot:
        me = await bot.get_me()
        assert me.username is not None, "Bot não autenticado — verifique o token."

        message = await bot.send_message(
            chat_id=TARGET_USER_ID,
            text=(
                "✅ *Teste de conectividade*\n\n"
                "O bot está rodando e consegue enviar mensagens!"
            ),
            parse_mode="Markdown",
        )

    assert message.message_id is not None
    assert message.chat.id == TARGET_USER_ID
    print(f"\nMensagem enviada com sucesso! message_id={message.message_id}")
