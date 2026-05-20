"""Message templates for the Album Copa 2026 Telegram bot.

Agent: Bot Interface Dev

Centralises every string sent to the user.  No messages may be hardcoded
anywhere outside this module.  Functions are preferred over module-level
constants so that values can be interpolated at call time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.figurinha import Figurinha
    from models.progresso import Progresso


def confirmar_adicionar(
    nome_selecao: str,
    codigo: str,
    quantidade: int,
    novo_saldo: int,
) -> str:
    """Format a success confirmation after adding stickers.

    Args:
        nome_selecao: Full team/section name in Portuguese.
        codigo: Canonical sticker code (e.g. ``"BRA-1"``).
        quantidade: Number of stickers that were added.
        novo_saldo: Updated stock balance after the operation.

    Returns:
        Formatted confirmation message string.
    """
    return (
        f"✅ *{codigo}* ({nome_selecao}) adicionada!\n"
        f"+{quantidade} figurinha(s) | Saldo atual: *{novo_saldo}*"
    )


def confirmar_remover(
    nome_selecao: str,
    codigo: str,
    quantidade: int,
    novo_saldo: int,
) -> str:
    """Format a success confirmation after removing stickers.

    Args:
        nome_selecao: Full team/section name in Portuguese.
        codigo: Canonical sticker code (e.g. ``"BRA-1"``).
        quantidade: Number of stickers that were removed.
        novo_saldo: Updated stock balance after the operation.

    Returns:
        Formatted confirmation message string.
    """
    return (
        f"✅ *{codigo}* ({nome_selecao}) removida!\n"
        f"-{quantidade} figurinha(s) | Saldo atual: *{novo_saldo}*"
    )


def solicitar_codigo() -> str:
    """Prompt the user to type a sticker code.

    Returns:
        Instruction message asking for a sticker code.
    """
    return (
        "ℹ️ Digite o código ou nome da figurinha.\n"
        "Exemplos: `BRA-1`, `Brasil 1`, `FWC 0`, `CC-14`\n\n"
        "Envie /cancelar para cancelar."
    )


def solicitar_quantidade_adicionar(
    nome_selecao: str,
    codigo: str,
    saldo_atual: int,
) -> str:
    """Confirm the identified sticker and ask how many to add.

    Args:
        nome_selecao: Full team/section name in Portuguese.
        codigo: Canonical sticker code.
        saldo_atual: Current stock balance for the sticker.

    Returns:
        Message confirming the sticker and requesting a quantity.
    """
    return (
        f"ℹ️ Figurinha identificada: *{codigo}* ({nome_selecao})\n"
        f"Saldo atual: *{saldo_atual}*\n\n"
        "Quantas figurinhas deseja *adicionar*?\n"
        "Envie /cancelar para cancelar."
    )


def solicitar_quantidade_remover(
    nome_selecao: str,
    codigo: str,
    saldo_atual: int,
) -> str:
    """Confirm the identified sticker and ask how many to remove.

    Args:
        nome_selecao: Full team/section name in Portuguese.
        codigo: Canonical sticker code.
        saldo_atual: Current stock balance for the sticker.

    Returns:
        Message confirming the sticker and requesting a quantity.
    """
    return (
        f"ℹ️ Figurinha identificada: *{codigo}* ({nome_selecao})\n"
        f"Saldo atual: *{saldo_atual}*\n\n"
        "Quantas figurinhas deseja *remover*?\n"
        "Envie /cancelar para cancelar."
    )


def erro_codigo_invalido(entrada: str, detalhe: str) -> str:
    """Inform the user that their input could not be parsed as a sticker code.

    Args:
        entrada: Raw text provided by the user.
        detalhe: Technical detail from the parser exception message.

    Returns:
        Error message asking the user to try again.
    """
    return (
        f"❌ Código inválido: `{entrada}`\n"
        f"{detalhe}\n\n"
        "Tente novamente ou envie /cancelar para cancelar."
    )


def erro_quantidade_invalida() -> str:
    """Inform the user that the quantity entered is not a valid positive integer.

    Returns:
        Error message asking the user to enter a valid quantity.
    """
    return (
        "❌ Quantidade inválida.\n"
        "Digite um número inteiro positivo (ex.: `1`, `5`).\n\n"
        "Tente novamente ou envie /cancelar para cancelar."
    )


def erro_saldo_insuficiente(codigo: str, saldo_atual: int, solicitado: int) -> str:
    """Inform the user that the stock is insufficient for the requested removal.

    Args:
        codigo: Canonical sticker code.
        saldo_atual: Current stock balance.
        solicitado: Quantity the user attempted to remove.

    Returns:
        Error message with current balance and a prompt to retry.
    """
    return (
        f"❌ Saldo insuficiente para *{codigo}*.\n"
        f"Disponível: *{saldo_atual}* | Solicitado: *{solicitado}*\n\n"
        "Digite uma quantidade menor ou envie /cancelar para cancelar."
    )


def erro_figurinha_nao_encontrada(codigo: str) -> str:
    """Inform the user that no sticker with the given code exists in the database.

    Args:
        codigo: Canonical sticker code that was not found.

    Returns:
        Error message for a missing sticker record.
    """
    return (
        f"❌ Figurinha *{codigo}* não encontrada no banco de dados.\n"
        "Verifique o código e tente novamente."
    )


def erro_generico() -> str:
    """Generic error message for unexpected failures.

    Returns:
        Generic error message asking the user to try again later.
    """
    return (
        "❌ Ocorreu um erro inesperado.\n"
        "Tente novamente mais tarde ou contate o administrador."
    )


def operacao_cancelada() -> str:
    """Confirm that the current operation has been cancelled.

    Returns:
        Cancellation confirmation message.
    """
    return "ℹ️ Operação cancelada."


def boas_vindas() -> str:
    """Welcome message sent in response to the /start command.

    Returns:
        Welcome message listing available commands.
    """
    return (
        "👋 Bem-vindo ao *Bot Figurinhas Copa 2026*!\n\n"
        "Comandos disponíveis:\n"
        "• /adicionar — Adicionar figurinha ao estoque\n"
        "• /adicionar\\_lote — Adicionar várias figurinhas de uma vez\n"
        "• /remover — Remover figurinha do estoque\n"
        "• /progresso — Ver % de completude do álbum\n"
        "• /faltantes — Ver figurinhas que faltam por país\n"
        "• /repetidas — Ver figurinhas repetidas\n"
        "• /cancelar — Cancelar a operação em andamento"
    )


def solicitar_lote() -> str:
    """Prompt the user to send a list of sticker codes, one per line.

    Returns:
        Instruction message for the batch-add flow.
    """
    return (
        "ℹ️ Envie os códigos das figurinhas, *um por linha*.\n"
        "Cada figurinha receberá +1 unidade.\n\n"
        "Exemplo:\n"
        "`BRA-1`\n"
        "`Argentina 5`\n"
        "`GER-3`\n\n"
        "Envie /cancelar para cancelar."
    )


def formatar_resultado_lote(
    sucesso: list,
    falhas: list[tuple[str, str]],
) -> str:
    """Format the result of a batch-add operation.

    Args:
        sucesso: List of :class:`~models.figurinha.Figurinha` objects that
            were successfully updated.
        falhas: List of ``(entrada_bruta, error_message)`` pairs for entries
            that could not be processed.

    Returns:
        Multi-line Markdown summary of the batch result.
    """
    linhas: list[str] = []
    if sucesso:
        linhas.append(f"✅ *Adicionadas com sucesso ({len(sucesso)}):*")
        for fig in sucesso:
            linhas.append(
                f"• {fig.codigo_figurinha} ({fig.nome_selecao}) → saldo: *{fig.quantidade}*"
            )
    if falhas:
        if linhas:
            linhas.append("")
        linhas.append(f"❌ *Não processadas ({len(falhas)}):*")
        for entrada, motivo in falhas:
            linhas.append(f"• `{entrada}` — {motivo}")
    return "\n".join(linhas)


def formatar_progresso(progresso: Progresso) -> str:
    """Format the album completion progress for display.

    Args:
        progresso: :class:`~models.progresso.Progresso` with aggregated stats.

    Returns:
        Multi-line Markdown string summarising album completion.
    """
    return (
        "📊 *Progresso do Álbum Copa 2026*\n\n"
        f"🎯 {progresso.percentual}% completo\n"
        f"✅ {progresso.tipos_possuidos} de {progresso.total_album} figurinhas únicas\n"
        f"📦 {f'{progresso.total_exemplares:,}'.replace(',', '.')} exemplares no total\n"
        f"❌ {progresso.tipos_faltantes} figurinhas ainda faltando"
    )


def _formatar_grupo_faltantes(grupo: str, selecoes: dict[str, list[Figurinha]]) -> str:
    """Format a single grupo block for the faltantes message.

    Args:
        grupo: Album group label (e.g. ``"A"``).
        selecoes: Dict mapping ``nome_selecao`` to the list of missing figurinhas.

    Returns:
        Formatted block with group header and per-selection lines.
    """
    linhas = [f"*Grupo {grupo}*"]
    for nome_selecao in sorted(selecoes):
        count = len(selecoes[nome_selecao])
        linhas.append(f"  • {nome_selecao} — {count} faltando")
    return "\n".join(linhas)


def formatar_faltantes(
    agrupados: dict[str, dict[str, list[Figurinha]]],
    progresso: Progresso,
) -> str:
    """Format the missing stickers list grouped by album group and selection.

    Args:
        agrupados: Nested dict ``{grupo: {nome_selecao: [Figurinha, ...]}}``.
        progresso: :class:`~models.progresso.Progresso` for summary counts.

    Returns:
        Multi-line Markdown string listing missing stickers per group.
        Returns a completion congratulation when ``agrupados`` is empty.
    """
    if not agrupados:
        return "✅ Parabéns! Álbum completo!"

    cabecalho = (
        f"📋 *Figurinhas Faltantes — "
        f"{progresso.tipos_faltantes} de {progresso.total_album}*\n"
    )
    blocos = [_formatar_grupo_faltantes(g, agrupados[g]) for g in sorted(agrupados)]
    return cabecalho + "\n" + "\n\n".join(blocos)


def formatar_repetidas(repetidas: list[Figurinha]) -> str:
    """Format the list of repeated stickers (quantidade > 1).

    Args:
        repetidas: List of :class:`~models.figurinha.Figurinha` with ``quantidade > 1``.

    Returns:
        Multi-line Markdown string listing each repeated sticker.
        Returns an informational message when the list is empty.
    """
    if not repetidas:
        return "ℹ️ Nenhuma figurinha repetida."

    cabecalho = f"🔄 *Figurinhas Repetidas — {len(repetidas)} tipos*\n"
    linhas = [
        f"• {f.codigo_figurinha} ({f.nome_selecao}) — {f.quantidade}×"
        for f in repetidas
    ]
    return cabecalho + "\n" + "\n".join(linhas)
