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

# ---------------------------------------------------------------------------
# Flag emoji mapping  (keyed by codigo_selecao)
# ---------------------------------------------------------------------------

_BANDEIRAS: dict[str, str] = {
    "MEX": "🇲🇽", "RSA": "🇿🇦", "KOR": "🇰🇷", "CZE": "🇨🇿",
    "CAN": "🇨🇦", "BIH": "🇧🇦", "QAT": "🇶🇦", "SUI": "🇨🇭",
    "BRA": "🇧🇷", "MAR": "🇲🇦", "HAI": "🇭🇹", "SCO": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "USA": "🇺🇸", "PAR": "🇵🇾", "AUS": "🇦🇺", "TUR": "🇹🇷",
    "GER": "🇩🇪", "CUW": "🇨🇼", "CIV": "🇨🇮", "ECU": "🇪🇨",
    "NED": "🇳🇱", "JPN": "🇯🇵", "SWE": "🇸🇪", "TUN": "🇹🇳",
    "BEL": "🇧🇪", "EGY": "🇪🇬", "IRN": "🇮🇷", "NZL": "🇳🇿",
    "ESP": "🇪🇸", "CPV": "🇨🇻", "KSA": "🇸🇦", "URU": "🇺🇾",
    "FRA": "🇫🇷", "SEN": "🇸🇳", "IRQ": "🇮🇶", "NOR": "🇳🇴",
    "ARG": "🇦🇷", "ALG": "🇩🇿", "AUT": "🇦🇹", "JOR": "🇯🇴",
    "POR": "🇵🇹", "COD": "🇨🇩", "UZB": "🇺🇿", "COL": "🇨🇴",
    "ENG": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "CRO": "🇭🇷", "GHA": "🇬🇭", "PAN": "🇵🇦",
    "FWC": "🏆", "CC": "🥤",
}


def bandeira(codigo_selecao: str) -> str:
    """Return the flag emoji for the given selection code, or empty string.

    Args:
        codigo_selecao: Two-to-three-letter selection code (e.g. ``"BRA"``).

    Returns:
        Flag emoji string, or ``""`` when the code is unknown.
    """
    return _BANDEIRAS.get(codigo_selecao, "")


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


def formatar_dados_usuario(dados: dict) -> str:
    """Format the user data summary for /consulta.

    Args:
        dados: Dict returned by ``FigurinhaService.consultar_dados_usuario``.

    Returns:
        Formatted Markdown message with user data summary.
    """
    primeira = dados["primeira_movimentacao"]
    ultima = dados["ultima_movimentacao"]
    primeira_txt = primeira.strftime("%d/%m/%Y") if primeira else "—"
    ultima_txt = ultima.strftime("%d/%m/%Y") if ultima else "—"

    return (
        "🔐 *Seus dados armazenados*\n\n"
        f"• *Telegram ID:* `{dados['telegram_user_id']}`\n"
        f"• *Figurinhas no álbum:* {dados['total_figurinhas']}\n"
        f"• *Figurinhas possuídas:* {dados['possuidas']}\n"
        f"• *Total de exemplares:* {dados['total_exemplares']}\n"
        f"• *Movimentações registradas:* {dados['total_movimentacoes']}\n"
        f"• *Primeira movimentação:* {primeira_txt}\n"
        f"• *Última movimentação:* {ultima_txt}\n\n"
        "Para solicitar a exclusão dos seus dados, use /excluir\\_usuario."
    )


def confirmacao_exclusao() -> str:
    """Confirmation prompt shown before deleting a user's data.

    Returns:
        Warning message asking the user to confirm deletion.
    """
    return (
        "⚠️ *ATENÇÃO!!*\n\n"
        "Os seus dados serão excluídos de forma *PERMANENTE, DEFINITIVA e IRRECUPERÁVEL.*\n\n"
        "Deseja realmente prosseguir?\n\n"
        "Digite *Sim* para confirmar ou *Não* para cancelar."
    )


def confirmar_exclusao_realizada() -> str:
    """Confirmation message shown after successful user data deletion.

    Returns:
        Success message informing the user their data was deleted.
    """
    return (
        "✅ Seus dados foram excluídos com sucesso.\n"
        "Seu álbum e histórico de movimentações foram removidos permanentemente.\n\n"
        "Se quiser usar o bot novamente, basta enviar /start."
    )


def cancelar_exclusao() -> str:
    """Message shown when the user cancels the deletion flow.

    Returns:
        Cancellation confirmation message for the deletion flow.
    """
    return "ℹ️ Exclusão cancelada. Seus dados foram mantidos."


def solicitar_codigo_busca() -> str:
    """Prompt the user to type a sticker code for the /buscar lookup.

    Returns:
        Instruction message asking for a sticker code.
    """
    return (
        "🔍 Digite o código ou nome da figurinha que deseja buscar.\n"
        "Exemplos: `BRA-1`, `Brasil 1`, `FWC 0`, `CC-14`\n\n"
        "Envie /cancelar para cancelar."
    )


def formatar_busca(figurinha: "Figurinha") -> str:
    """Format the result of a single sticker lookup (/buscar).

    Args:
        figurinha: The found :class:`~models.figurinha.Figurinha` instance.

    Returns:
        Formatted message reflecting the user's current stock for that sticker.
    """
    codigo = figurinha.codigo_figurinha
    nome = figurinha.nome_selecao
    qtd = figurinha.quantidade

    if qtd == 0:
        return (
            f"❌ *{codigo}* ({nome})\n"
            "Você ainda não tem essa figurinha.\n"
            "Digite /adicionar para registrá-la quando encontrá-la."
        )
    if qtd == 1:
        return (
            f"✅ Você já possui essa figurinha!\n"
            f"*{codigo}* ({nome})\n\n"
            "Se tiver mais figurinhas dessa, digite /adicionar para registrar a quantidade."
        )
    return (
        f"⚠️ Figurinha repetida.\n"
        f"Você já tem *{qtd}* de *{codigo}* ({nome})."
    )


def solicitar_pais() -> str:
    """Prompt the user to type a country name for the /buscar_pais lookup.

    Returns:
        Instruction message asking for a country name.
    """
    return (
        "🔍 Digite o nome do país que deseja buscar.\n"
        "Exemplos: `Brasil`, `Argentina`, `Alemanha`, `Costa do Marfim`\n\n"
        "Envie /cancelar para cancelar."
    )


def formatar_busca_pais(
    nome_selecao: str,
    codigo_selecao: str,
    figurinhas: "list[Figurinha]",
) -> str:
    """Format the full sticker breakdown for a given country (/buscar_pais).

    Separates the figurinhas into three sections — owned (qty == 1),
    repeated (qty > 1), and missing (qty == 0).

    Args:
        nome_selecao: Full country name in Portuguese.
        codigo_selecao: Short country code, e.g. ``"BRA"``.
        figurinhas: All figurinhas for the country ordered by ``numero``.

    Returns:
        Formatted Markdown message with three sticker-status sections.
    """
    flag = bandeira(codigo_selecao)
    prefix = f"{flag} " if flag else ""

    tem = [f for f in figurinhas if f.quantidade >= 1]
    repetidas = [f for f in figurinhas if f.quantidade > 1]
    faltam = [f for f in figurinhas if f.quantidade == 0]

    linhas: list[str] = [
        f"*Busca por país*",
        f"{prefix}*{nome_selecao}*",
        "",
        f"✅ *Já tem*",
    ]
    if tem:
        linhas.extend(f.codigo_figurinha for f in tem)
    else:
        linhas.append("_(nenhuma)_")

    linhas += ["", "⚠️ *Repetidas*"]
    if repetidas:
        linhas.extend(f"{f.codigo_figurinha} (×{f.quantidade - 1})" for f in repetidas)
    else:
        linhas.append("_(nenhuma)_")

    linhas += ["", "❌ *Faltam*"]
    if faltam:
        linhas.extend(f.codigo_figurinha for f in faltam)
    else:
        linhas.append("_(nenhuma — país completo! 🎉)_")

    return "\n".join(linhas)


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
        "• /remover\\_lote — Remover várias figurinhas de uma vez\n"
        "• /progresso — Ver % de completude do álbum\n"
        "• /faltantes — Ver figurinhas que faltam por país\n"
        "• /repetidas — Ver figurinhas repetidas\n"
        "• /buscar — Buscar uma figurinha específica\n"
        "• /buscar\\_pais — Ver todas as figurinhas de um país\n"
        "• /consulta — Ver seus dados armazenados\n"
        "• /excluir\\_usuario — Excluir todos os seus dados\n"
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


def solicitar_lote_remover() -> str:
    """Prompt the user to send a list of sticker codes to remove, one per line.

    Returns:
        Instruction message for the batch-remove flow.
    """
    return (
        "ℹ️ Envie os códigos das figurinhas, *um por linha*.\n"
        "Cada figurinha terá -1 unidade.\n\n"
        "Exemplo:\n"
        "`BRA-1`\n"
        "`Argentina 5`\n"
        "`GER-3`\n\n"
        "Envie /cancelar para cancelar."
    )


def formatar_resultado_remover_lote(
    sucesso: list,
    falhas: list[tuple[str, str]],
) -> str:
    """Format the result of a batch-remove operation.

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
        linhas.append(f"✅ *Removidas com sucesso ({len(sucesso)}):*")
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


def _formatar_top3(itens: tuple[tuple[str, int], ...], vazio: str) -> str:
    """Render a top-3 selection list as bullet lines.

    Args:
        itens: Sequence of ``(nome_selecao, qtd_faltantes)`` tuples.
        vazio: Line to use when *itens* is empty.

    Returns:
        Multi-line string with one bullet per item, or *vazio* when empty.
    """
    if not itens:
        return vazio
    return "\n".join(f"• {nome}: {qtd} faltando" for nome, qtd in itens)


def formatar_progresso(progresso: Progresso) -> str:
    """Format the album completion progress for display.

    Args:
        progresso: :class:`~models.progresso.Progresso` with aggregated stats.

    Returns:
        Multi-line Markdown string summarising album completion.
    """
    _sem_incompletas = "• Nenhuma seleção incompleta 🎉"
    proximos = _formatar_top3(progresso.top3_proximos, _sem_incompletas)
    distantes = _formatar_top3(progresso.top3_distantes, _sem_incompletas)

    brilhantes = progresso.brilhantes_faltantes
    brilhantes_txt = (
        " ".join(brilhantes) if brilhantes else "• Todos os brilhantes coletados! ✨"
    )
    cc = progresso.cc_faltantes
    cc_txt = " ".join(cc) if cc else "• Nenhum CC faltando! 🎉"

    return (
        "*Seu álbum Copa 2026* 🏆\n\n"
        f"📊 *{progresso.percentual}% completo*\n"
        f"📌 {progresso.tipos_possuidos} de 994 figurinhas únicas\n"
        f"❌ {progresso.tipos_faltantes} figurinhas ainda faltando\n"
        f"📦 {progresso.total_exemplares} figurinhas no total\n\n"
        f"🌍 *{progresso.paises_completos} países completos*\n\n"
        f"🔜 *Mais próximos de completar:*\n{proximos}\n\n"
        f"🔚 *Mais distantes de completar:*\n{distantes}\n\n"
        f"⭐ *Brilhantes faltantes ({len(brilhantes)}):*\n{brilhantes_txt}\n\n"
        f"🥤 *CC faltantes ({len(cc)}):*\n{cc_txt}"
    )


def formatar_faltantes(
    grupos: list[tuple[str, list[tuple[str, str, list[Figurinha]]]]],
    progresso: Progresso,
) -> list[str]:
    """Format the missing stickers list grouped by album group.

    Produces one Telegram message per album group (A–L, FWC, CC).  Each
    message starts with a bold group header followed by one country block per
    country in the group.

    Args:
        grupos: Page-ordered list of ``(group_header, [(nome, codigo, figs)])``
            as returned by ``AlbumQueryService.faltantes_agrupados``.
        progresso: :class:`~models.progresso.Progresso` (used only when
            ``grupos`` is empty to decide the completion message).

    Returns:
        List of Markdown strings, one per album group.  When the album is
        complete the list contains a single congratulatory string.
    """
    if not grupos:
        return ["✅ Parabéns! Álbum completo!"]

    mensagens: list[str] = []
    for group_header, secoes in grupos:
        linhas: list[str] = [f"*Faltantes - {group_header}:*"]
        for nome, codigo, figs in secoes:
            flag = bandeira(codigo)
            prefix = f"{flag} " if flag else ""
            linhas.append(f"\n*{prefix}{nome}:*")
            linhas.extend(f.codigo_figurinha for f in figs)
        mensagens.append("\n".join(linhas))
    return mensagens


def formatar_repetidas(
    grupos: list[tuple[str, list[tuple[str, str, list[Figurinha]]]]],
) -> list[str]:
    """Format repeated stickers grouped by album group.

    Produces one Telegram message per album group (A–L, FWC, CC).  Each
    message starts with a bold group header followed by one country block per
    country, listing each repeated sticker code.

    Args:
        grupos: Page-ordered list of ``(group_header, [(nome, codigo, figs)])``
            as returned by ``AlbumQueryService.repetidas_agrupadas``.

    Returns:
        List of Markdown strings, one per album group.  Returns a single
        informational message when there are no repeated stickers.
    """
    if not grupos:
        return ["ℹ️ Nenhuma figurinha repetida."]

    mensagens: list[str] = []
    for group_header, secoes in grupos:
        linhas: list[str] = [f"*Repetidas - {group_header}:*"]
        for nome, codigo, figs in secoes:
            flag = bandeira(codigo)
            prefix = f"{flag} " if flag else ""
            linhas.append(f"\n*{prefix}{nome}:*")
            linhas.extend(f.codigo_figurinha for f in figs)
        mensagens.append("\n".join(linhas))
    return mensagens
