"""Controller layer bridging Telegram handlers and the domain service.

Agent: Bot Interface Dev

:class:`BotController` receives raw user input from handlers, delegates to
:class:`~services.figurinha_service.FigurinhaService`, and returns formatted
strings via :mod:`views.message_templates`.

It **never raises exceptions** to its callers — every domain exception is
caught here and converted into a user-friendly message.
"""

import logging
from typing import Optional

from exceptions.domain_exceptions import (
    AlbumCopaError,
    CodigoInvalidoError,
    FigurinhaNaoEncontradaError,
    QuantidadeInsuficienteError,
)
from models.figurinha import Figurinha
from services.album_query_service import AlbumQueryService
from services.figurinha_service import FigurinhaService
from views import message_templates as tmpl

logger = logging.getLogger(__name__)


class BotController:
    """Orchestrates parser → service → message_templates for Telegram handlers.

    Args:
        figurinha_service: Injected service handling sticker stock operations.
        album_query_service: Injected service for read-only album queries.
    """

    def __init__(
        self,
        figurinha_service: FigurinhaService,
        album_query_service: AlbumQueryService,
    ) -> None:
        """Initialise the controller with injected services.

        Args:
            figurinha_service: Concrete or mock service for stock operations.
            album_query_service: Concrete or mock service for album queries.
        """
        self._service = figurinha_service
        self._query_service = album_query_service

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _garantir_album(self, telegram_user_id: int, telegram_username: str) -> None:
        """Ensure the user's album is initialised before any query or mutation.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username (for logging).
        """
        self._service.garantir_album_inicializado(telegram_user_id, telegram_username)

    def _tratar_excecao_dominio(self, operacao: str, entrada_bruta: str, exc: Exception) -> str:
        """Convert a domain exception into a user-friendly error message.

        Handles the exception types common to all stock operations and logs
        an appropriate warning or error entry for each case.

        Args:
            operacao: Name of the calling operation (used in log messages).
            entrada_bruta: Raw text input supplied by the user.
            exc: The exception that was caught.

        Returns:
            Formatted error message ready to send to the user.
        """
        if isinstance(exc, CodigoInvalidoError):
            logger.warning("%s: codigo invalido entrada=%r: %s", operacao, entrada_bruta, exc)
            return tmpl.erro_codigo_invalido(entrada=entrada_bruta, detalhe=str(exc))
        if isinstance(exc, FigurinhaNaoEncontradaError):
            logger.warning("%s: figurinha nao encontrada: %s", operacao, exc)
            return tmpl.erro_figurinha_nao_encontrada(codigo=entrada_bruta)
        if isinstance(exc, QuantidadeInsuficienteError):
            logger.warning("%s: saldo insuficiente: %s", operacao, exc)
            return tmpl.erro_saldo_insuficiente(
                codigo=exc.codigo,
                saldo_atual=exc.saldo_atual,
                solicitado=exc.quantidade_solicitada,
            )
        if isinstance(exc, AlbumCopaError):
            logger.warning("%s: domain error: %s", operacao, exc)
            return tmpl.erro_generico()
        logger.exception("%s: unexpected error: %s", operacao, exc)
        return tmpl.erro_generico()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolver_codigo(
        self,
        entrada_bruta: str,
        telegram_user_id: int,
        telegram_username: str,
    ) -> tuple[Optional[Figurinha], Optional[str]]:
        """Validate and resolve a raw sticker code to a Figurinha record.

        Used by conversation handlers during the AGUARDANDO_CODIGO state to
        confirm that the user's input is parseable and exists in the database
        before advancing to the quantity state.

        Args:
            entrada_bruta: Raw text input from the user.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            A ``(figurinha, None)`` tuple on success, or ``(None, error_msg)``
            on failure.  The second element is always a ready-to-send string.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            figurinha = self._service.buscar_por_entrada(entrada_bruta, telegram_user_id)
            return figurinha, None
        except (CodigoInvalidoError, FigurinhaNaoEncontradaError) as exc:
            return None, tmpl.erro_codigo_invalido(entrada=entrada_bruta, detalhe=str(exc))
        except Exception:
            logger.exception("resolver_codigo: erro inesperado para entrada=%r", entrada_bruta)
            return None, tmpl.erro_generico()

    async def processar_adicionar(
        self,
        entrada_bruta: str,
        quantidade: int,
        telegram_user_id: int,
        telegram_username: str,
    ) -> str:
        """Add stickers and return a formatted result message.

        Delegates to :meth:`~services.figurinha_service.FigurinhaService.adicionar`
        and converts the returned :class:`~models.figurinha.Figurinha` into a
        human-readable confirmation.  All domain exceptions are caught and
        returned as error messages — this method never raises.

        Args:
            entrada_bruta: Raw text input from the user (code or name).
            quantidade: Number of stickers to add.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            Formatted success or error message ready to send.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            figurinha = self._service.adicionar(
                entrada_bruta=entrada_bruta,
                quantidade=quantidade,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
            )
            return tmpl.confirmar_adicionar(
                nome_selecao=figurinha.nome_selecao,
                codigo=figurinha.codigo_figurinha,
                quantidade=quantidade,
                novo_saldo=figurinha.quantidade,
            )
        except Exception as exc:
            return self._tratar_excecao_dominio("processar_adicionar", entrada_bruta, exc)

    async def processar_remover(
        self,
        entrada_bruta: str,
        quantidade: int,
        telegram_user_id: int,
        telegram_username: str,
    ) -> str:
        """Remove stickers and return a formatted result message.

        Delegates to :meth:`~services.figurinha_service.FigurinhaService.remover`
        and converts the returned :class:`~models.figurinha.Figurinha` into a
        human-readable confirmation.  All domain exceptions are caught and
        returned as error messages — this method never raises.

        Args:
            entrada_bruta: Raw text input from the user (code or name).
            quantidade: Number of stickers to remove.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            Formatted success or error message ready to send.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            figurinha = self._service.remover(
                entrada_bruta=entrada_bruta,
                quantidade=quantidade,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
            )
            return tmpl.confirmar_remover(
                nome_selecao=figurinha.nome_selecao,
                codigo=figurinha.codigo_figurinha,
                quantidade=quantidade,
                novo_saldo=figurinha.quantidade,
            )
        except Exception as exc:
            return self._tratar_excecao_dominio("processar_remover", entrada_bruta, exc)

    async def processar_adicionar_lote(
        self,
        entradas_brutas: list[str],
        telegram_user_id: int,
        telegram_username: str,
    ) -> str:
        """Process a batch of sticker codes, adding 1 of each.

        Delegates to :meth:`~services.figurinha_service.FigurinhaService.adicionar_lote`.
        Each entry is processed independently — partial success is reported.
        Never raises; always returns a formatted result string.

        Args:
            entradas_brutas: Raw sticker codes split from the user's message.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            Formatted batch result message ready to send.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            sucesso, falhas = self._service.adicionar_lote(
                entradas_brutas=entradas_brutas,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
            )
            return tmpl.formatar_resultado_lote(sucesso, falhas)
        except Exception:
            logger.exception("processar_adicionar_lote: unexpected error")
            return tmpl.erro_generico()

    async def processar_remover_lote(
        self,
        entradas_brutas: list[str],
        telegram_user_id: int,
        telegram_username: str,
    ) -> str:
        """Process a batch of sticker codes, removing 1 of each.

        Delegates to :meth:`~services.figurinha_service.FigurinhaService.remover_lote`.
        Each entry is processed independently — partial success is reported.
        Never raises; always returns a formatted result string.

        Args:
            entradas_brutas: Raw sticker codes split from the user's message.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            Formatted batch result message ready to send.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            sucesso, falhas = self._service.remover_lote(
                entradas_brutas=entradas_brutas,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
            )
            return tmpl.formatar_resultado_remover_lote(sucesso, falhas)
        except Exception:
            logger.exception("processar_remover_lote: unexpected error")
            return tmpl.erro_generico()

    def consultar_dados_usuario(self, telegram_user_id: int, telegram_username: str) -> str:
        """Return a formatted message with data stored for the user.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            Formatted message with the user's data summary.
        """
        try:
            dados = self._service.consultar_dados_usuario(telegram_user_id)
            return tmpl.formatar_dados_usuario(dados)
        except Exception:
            logger.exception("consultar_dados_usuario: unexpected error user=%d", telegram_user_id)
            return tmpl.erro_generico()

    def excluir_usuario(self, telegram_user_id: int, telegram_username: str) -> str:
        """Delete all data for the user and return a confirmation message.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            Formatted success or error message.
        """
        try:
            self._service.excluir_usuario(telegram_user_id)
            logger.info("excluir_usuario: user=%d username=%r deleted", telegram_user_id, telegram_username)
            return tmpl.confirmar_exclusao_realizada()
        except Exception:
            logger.exception("excluir_usuario: unexpected error user=%d", telegram_user_id)
            return tmpl.erro_generico()

    def consultar_buscar(
        self,
        entrada_bruta: str,
        telegram_user_id: int,
        telegram_username: str,
    ) -> str:
        """Look up a single sticker and return its stock status message.

        Args:
            entrada_bruta: Raw sticker code or name typed by the user.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            Formatted message reflecting quantity owned (0, 1, or >1).
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            figurinha = self._service.buscar_para_consulta(entrada_bruta, telegram_user_id)
            return tmpl.formatar_busca(figurinha)
        except Exception as exc:
            return self._tratar_excecao_dominio("consultar_buscar", entrada_bruta, exc)

    def consultar_buscar_pais(
        self,
        entrada_pais: str,
        telegram_user_id: int,
        telegram_username: str,
    ) -> str:
        """Return a full sticker breakdown for a given country.

        Args:
            entrada_pais: Country name or code typed by the user.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            Formatted message listing owned, repeated, and missing stickers.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            codigo_selecao = self._service.resolver_selecao(entrada_pais)
            figurinhas = self._query_service.buscar_por_selecao(codigo_selecao, telegram_user_id)
            nome = figurinhas[0].nome_selecao if figurinhas else entrada_pais
            return tmpl.formatar_busca_pais(nome, codigo_selecao, figurinhas)
        except Exception as exc:
            return self._tratar_excecao_dominio("consultar_buscar_pais", entrada_pais, exc)

    def consultar_progresso(self, telegram_user_id: int, telegram_username: str) -> str:
        """Return a formatted album completion progress message.

        Delegates to :class:`~services.album_query_service.AlbumQueryService`
        and formats the result via :func:`~views.message_templates.formatar_progresso`.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            Formatted progress message or a generic error message on failure.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            return tmpl.formatar_progresso(self._query_service.progresso_detalhado(telegram_user_id))
        except Exception:
            logger.exception("consultar_progresso: unexpected error")
            return tmpl.erro_generico()

    def consultar_faltantes(self, telegram_user_id: int, telegram_username: str) -> list[str]:
        """Return a list of formatted messages with missing stickers by group.

        Each element of the returned list corresponds to one album group and
        is intended to be sent as a separate Telegram message.  This avoids
        the Telegram 4 096-character per-message limit when the faltantes list
        is long.

        Delegates to :class:`~services.album_query_service.AlbumQueryService`
        and formats via :func:`~views.message_templates.formatar_faltantes`.

        Never raises — any exception is caught and converted into a
        single-element list containing a generic error message.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            List of Markdown strings ready to send, one per album group.
            Returns ``[tmpl.erro_generico()]`` on unexpected failure.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            agrupados = self._query_service.faltantes_agrupados(telegram_user_id)
            progresso = self._query_service.progresso(telegram_user_id)
            return tmpl.formatar_faltantes(agrupados, progresso)
        except Exception:
            logger.exception("consultar_faltantes: unexpected error")
            return [tmpl.erro_generico()]

    def consultar_repetidas(self, telegram_user_id: int, telegram_username: str) -> list[str]:
        """Return a formatted list of repeated stickers grouped by album group.

        Delegates to :class:`~services.album_query_service.AlbumQueryService`
        and formats via :func:`~views.message_templates.formatar_repetidas`.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username of the user.

        Returns:
            List of Markdown strings (one per album group) or a single-element
            list with a generic error message on failure.
        """
        try:
            self._garantir_album(telegram_user_id, telegram_username)
            agrupadas = self._query_service.repetidas_agrupadas(telegram_user_id)
            return tmpl.formatar_repetidas(agrupadas)
        except Exception:
            logger.exception("consultar_repetidas: unexpected error")
            return [tmpl.erro_generico()]
