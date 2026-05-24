"""Service layer for sticker (figurinha) stock operations.

Encapsulates the business rules for adding and removing stickers from the
user's collection.  All persistence is delegated to the injected repositories.
No SQL appears in this module.
"""

import logging

from exceptions.domain_exceptions import (
    CodigoInvalidoError,
    FigurinhaNaoEncontradaError,
    QuantidadeInsuficienteError,
)
from models.figurinha import Figurinha
from repositories.figurinha_repository import FigurinhaRepository
from seeds.album_data import ALBUM_GROUPS
from services.codigo_parser import CodigoParser
from services.movimentacao_service import MovimentacaoService

logger = logging.getLogger(__name__)


class FigurinhaService:
    """Handles sticker stock additions and removals.

    Args:
        figurinha_repository: Repository for reading and writing
            :class:`~models.figurinha.Figurinha` records.
        movimentacao_service: Service for registering stock movements.
        codigo_parser: Parser that normalises raw user input into canonical
            sticker codes.
    """

    def __init__(
        self,
        figurinha_repository: FigurinhaRepository,
        movimentacao_service: MovimentacaoService,
        codigo_parser: CodigoParser,
    ) -> None:
        """Initialise the service with injected collaborators.

        Args:
            figurinha_repository: Concrete or mock repository instance.
            movimentacao_service: Concrete or mock service instance.
            codigo_parser: Concrete or mock parser instance.
        """
        self._repo = figurinha_repository
        self._mov_service = movimentacao_service
        self._parser = codigo_parser

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validar_quantidade(self, quantidade: int) -> None:
        """Raise ValueError if quantidade is not a positive integer.

        Args:
            quantidade: Value provided by the caller.

        Raises:
            ValueError: If quantidade is less than 1.
        """
        if quantidade < 1:
            raise ValueError("Quantidade deve ser maior que zero")

    def _buscar_figurinha(self, codigo: str, telegram_user_id: int) -> Figurinha:
        """Fetch a figurinha by canonical code or raise if not found.

        Args:
            codigo: Canonical sticker code, e.g. ``"BRA-1"``.
            telegram_user_id: Numeric Telegram user ID scoping the lookup.

        Returns:
            The matching :class:`~models.figurinha.Figurinha` instance.

        Raises:
            FigurinhaNaoEncontradaError: If the code does not exist in the
                repository for this user.
        """
        figurinha = self._repo.find_by_codigo(codigo, telegram_user_id)
        if figurinha is None:
            raise FigurinhaNaoEncontradaError(
                f"Figurinha com código {codigo!r} não encontrada."
            )
        return figurinha

    def _persistir_mutacao(
        self,
        figurinha: Figurinha,
        tipo: str,
        quantidade: int,
        entrada_bruta: str,
        telegram_user_id: int,
        telegram_username: str,
    ) -> None:
        """Persist a quantity update and the corresponding movement record.

        Wraps the update, movement insert, and commit in a single try/except so
        that callers of :meth:`adicionar` and :meth:`remover` share identical
        error-handling behaviour.  Rolls back and re-raises on any failure.

        Args:
            figurinha: The sticker whose ``quantidade`` has already been mutated.
            tipo: Movement direction — ``"ENTRADA"`` or ``"SAIDA"``.
            quantidade: Number of stickers moved.
            entrada_bruta: Raw text input as received from Telegram.
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username``.
        """
        try:
            self._repo.update_quantidade(
                figurinha_id=figurinha.id,
                quantidade=figurinha.quantidade,
                telegram_user_id=telegram_user_id,
            )
            self._mov_service.registrar(
                figurinha_id=figurinha.id,
                tipo=tipo,
                quantidade=quantidade,
                entrada_bruta=entrada_bruta,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
            )
            self._repo.commit()
        except Exception:
            self._repo.rollback()
            raise

    @staticmethod
    def _build_stickers_payload() -> list[dict]:
        """Build the list of sticker dicts used to initialise a new album.

        Returns:
            List of dicts with keys ``grupo``, ``codigo_selecao``,
            ``nome_selecao``, ``numero``, ``codigo_figurinha``, ``pagina``
            for every sticker defined in :data:`seeds.album_data.ALBUM_GROUPS`.
        """
        return [
            {
                "grupo": group.grupo,
                "codigo_selecao": group.codigo_selecao,
                "nome_selecao": group.nome_selecao,
                "numero": numero,
                "codigo_figurinha": f"{group.codigo_selecao}-{numero}",
                "pagina": group.get_pagina(numero),
            }
            for group in ALBUM_GROUPS
            for numero in group.numeros
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def garantir_album_inicializado(
        self,
        telegram_user_id: int,
        telegram_username: str,
    ) -> None:
        """Initialise the user's album on first use.

        Checks whether the user already has sticker rows in the database. If not,
        inserts all 994 sticker records with quantidade=0.

        Args:
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram @username (for logging).
        """
        if self._repo.usuario_tem_album(telegram_user_id):
            return

        logger.info("garantir_album_inicializado: initialising album for user=%r", telegram_username)
        stickers = self._build_stickers_payload()
        try:
            self._repo.inicializar_album(telegram_user_id, stickers)
            self._repo.commit()
            logger.info(
                "garantir_album_inicializado: %d stickers created for user=%r",
                len(stickers),
                telegram_username,
            )
        except Exception:
            self._repo.rollback()
            logger.exception(
                "garantir_album_inicializado: rollback after error for user=%r", telegram_username
            )
            raise

    def adicionar(
        self,
        entrada_bruta: str,
        quantidade: int,
        telegram_user_id: int,
        telegram_username: str,
    ) -> Figurinha:
        """Normaliza o código, valida, incrementa a quantidade e registra a movimentação.

        Args:
            entrada_bruta: Raw text typed by the user (e.g. ``"Brasil 1"``).
            quantidade: Number of stickers to add (must be ≥ 1).
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            The updated :class:`~models.figurinha.Figurinha` instance with the
            new quantity already applied.

        Raises:
            ValueError: If *quantidade* is less than 1.
            CodigoInvalidoError: If *entrada_bruta* cannot be parsed into a
                valid sticker code.
            FigurinhaNaoEncontradaError: If the parsed code does not exist in
                the repository.
        """
        self._validar_quantidade(quantidade)
        codigo = self._parser.normalizar(entrada_bruta)
        figurinha = self._buscar_figurinha(codigo, telegram_user_id)
        figurinha.quantidade += quantidade
        self._persistir_mutacao(figurinha, "ENTRADA", quantidade, entrada_bruta, telegram_user_id, telegram_username)
        logger.debug("adicionar: codigo=%r nova_quantidade=%d user=%r", codigo, figurinha.quantidade, telegram_username)
        return figurinha

    def remover(
        self,
        entrada_bruta: str,
        quantidade: int,
        telegram_user_id: int,
        telegram_username: str,
    ) -> Figurinha:
        """Normaliza o código, valida saldo, decrementa e registra a movimentação.

        Args:
            entrada_bruta: Raw text typed by the user (e.g. ``"Brasil 1"``).
            quantidade: Number of stickers to remove (must be ≥ 1).
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            The updated :class:`~models.figurinha.Figurinha` instance with the
            new quantity already applied.

        Raises:
            ValueError: If *quantidade* is less than 1.
            CodigoInvalidoError: If *entrada_bruta* cannot be parsed into a
                valid sticker code.
            FigurinhaNaoEncontradaError: If the parsed code does not exist in
                the repository.
            QuantidadeInsuficienteError: If the current stock is lower than
                *quantidade*.
        """
        self._validar_quantidade(quantidade)
        codigo = self._parser.normalizar(entrada_bruta)
        figurinha = self._buscar_figurinha(codigo, telegram_user_id)

        if figurinha.quantidade < quantidade:
            raise QuantidadeInsuficienteError(
                codigo=figurinha.codigo_figurinha,
                saldo_atual=figurinha.quantidade,
                quantidade_solicitada=quantidade,
            )

        figurinha.quantidade -= quantidade
        self._persistir_mutacao(figurinha, "SAIDA", quantidade, entrada_bruta, telegram_user_id, telegram_username)
        logger.debug("remover: codigo=%r nova_quantidade=%d user=%r", codigo, figurinha.quantidade, telegram_username)
        return figurinha

    def adicionar_lote(
        self,
        entradas_brutas: list[str],
        telegram_user_id: int,
        telegram_username: str,
    ) -> tuple[list[Figurinha], list[tuple[str, str]]]:
        """Add 1 of each sticker in a batch, processing each line independently.

        Iterates over *entradas_brutas*, skips blank lines, and calls
        :meth:`adicionar` with ``quantidade=1`` for each entry.  Failures for
        individual entries are collected and returned rather than aborting the
        whole batch.

        Args:
            entradas_brutas: List of raw sticker codes (one per original line).
            telegram_user_id: Numeric Telegram user ID.
            telegram_username: Telegram ``@username`` of the user.

        Returns:
            A tuple ``(sucesso, falhas)`` where *sucesso* is a list of updated
            :class:`~models.figurinha.Figurinha` objects and *falhas* is a list
            of ``(entrada_bruta, error_message)`` pairs.
        """
        sucesso: list[Figurinha] = []
        falhas: list[tuple[str, str]] = []
        for entrada in entradas_brutas:
            entrada = entrada.strip()
            if not entrada:
                continue
            try:
                fig = self.adicionar(
                    entrada_bruta=entrada,
                    quantidade=1,
                    telegram_user_id=telegram_user_id,
                    telegram_username=telegram_username,
                )
                sucesso.append(fig)
            except (CodigoInvalidoError, FigurinhaNaoEncontradaError, ValueError) as exc:
                falhas.append((entrada, str(exc)))
            except Exception:
                logger.exception("adicionar_lote: erro inesperado para entrada=%r", entrada)
                falhas.append((entrada, "Erro inesperado"))
        return sucesso, falhas

    def consultar_dados_usuario(self, telegram_user_id: int) -> dict:
        """Return a summary of data stored for the given user.

        Args:
            telegram_user_id: Numeric Telegram user ID.

        Returns:
            Dict with user data summary from the repository.
        """
        return self._repo.get_dados_usuario(telegram_user_id)

    def excluir_usuario(self, telegram_user_id: int) -> tuple[int, int]:
        """Delete all data for the given user and commit the transaction.

        Args:
            telegram_user_id: Numeric Telegram user ID.

        Returns:
            Tuple ``(movimentacoes_deleted, figurinhas_deleted)``.
        """
        try:
            resultado = self._repo.excluir_usuario(telegram_user_id)
            self._repo.commit()
            return resultado
        except Exception:
            self._repo.rollback()
            raise

    def resolver_selecao(self, entrada_bruta: str) -> str:
        """Resolve a country name or bare code to its canonical codigo_selecao.

        Args:
            entrada_bruta: Country name or code typed by the user.

        Returns:
            Canonical ``codigo_selecao`` string, e.g. ``"BRA"``.

        Raises:
            CodigoInvalidoError: If the entry cannot be matched to any known
                selection in the Copa 2026 album.
        """
        return self._parser.resolver_selecao(entrada_bruta)

    def buscar_para_consulta(self, entrada_bruta: str, telegram_user_id: int) -> Figurinha:
        """Parse a sticker code and fetch the record without locking the row.

        Intended for read-only lookups (e.g. /buscar).  Uses
        :meth:`~repositories.figurinha_repository.FigurinhaRepository.find_by_codigo_readonly`
        so it does not block concurrent write operations on the same row.

        Args:
            entrada_bruta: Raw text typed by the user (any accepted format).
            telegram_user_id: Numeric Telegram user ID scoping the lookup.

        Returns:
            The matching :class:`~models.figurinha.Figurinha` instance.

        Raises:
            CodigoInvalidoError: If the code cannot be parsed.
            FigurinhaNaoEncontradaError: If the sticker does not exist for the user.
        """
        codigo = self._parser.normalizar(entrada_bruta)
        figurinha = self._repo.find_by_codigo_readonly(codigo, telegram_user_id)
        if figurinha is None:
            raise FigurinhaNaoEncontradaError(
                f"Figurinha com código {codigo!r} não encontrada."
            )
        return figurinha

    def buscar_por_entrada(self, entrada_bruta: str, telegram_user_id: int) -> Figurinha:
        """Normaliza o código de entrada e retorna a Figurinha correspondente.

        Args:
            entrada_bruta: Texto digitado pelo usuário (qualquer formato aceito).
            telegram_user_id: Numeric Telegram user ID scoping the lookup.

        Returns:
            A Figurinha encontrada no banco.

        Raises:
            CodigoInvalidoError: Se o código não puder ser normalizado.
            FigurinhaNaoEncontradaError: Se a figurinha não existir no banco.
        """
        codigo = self._parser.normalizar(entrada_bruta)
        return self._buscar_figurinha(codigo, telegram_user_id)
