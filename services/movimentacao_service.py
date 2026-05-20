"""Service layer for stock movement (movimentacao) operations.

Encapsulates business logic for creating movement records.  All persistence
is delegated to :class:`repositories.movimentacao_repository.MovimentacaoRepository`.
No SQL appears in this module.
"""

import logging
from typing import Optional

from models.movimentacao import Movimentacao
from repositories.movimentacao_repository import MovimentacaoRepository

logger = logging.getLogger(__name__)


class MovimentacaoService:
    """Handles creation of stock movement records.

    Args:
        movimentacao_repository: Repository responsible for persisting
            :class:`~models.movimentacao.Movimentacao` records.
    """

    def __init__(self, movimentacao_repository: MovimentacaoRepository) -> None:
        """Initialise the service with an injected repository.

        Args:
            movimentacao_repository: Concrete or mock repository instance.
        """
        self._repo = movimentacao_repository

    def registrar(
        self,
        figurinha_id: int,
        tipo: str,
        quantidade: int,
        entrada_bruta: str,
        telegram_user_id: int,
        telegram_username: str,
        origem: str = "MANUAL",
        observacao: Optional[str] = None,
    ) -> Movimentacao:
        """Cria e persiste um registro de movimentação.

        Builds a :class:`~models.movimentacao.Movimentacao` object from the
        provided arguments and delegates persistence to the repository.  Any
        exception raised by the repository propagates to the caller unchanged.

        Args:
            figurinha_id: Primary key of the sticker involved in the movement.
            tipo: Movement direction — ``"ENTRADA"`` (stock in) or
                ``"SAIDA"`` (stock out).
            quantidade: Number of stickers moved (must be positive).
            entrada_bruta: Raw text input as received from the Telegram message.
            telegram_user_id: Numeric Telegram user ID that triggered the action.
            telegram_username: Telegram ``@username`` of the user.
            origem: Source of the movement, defaults to ``"MANUAL"``.
            observacao: Optional free-text note attached to the movement.

        Returns:
            The persisted :class:`~models.movimentacao.Movimentacao` instance.

        Raises:
            Exception: Any exception raised by the repository is re-raised
                without modification.
        """
        logger.debug(
            "registrar: figurinha_id=%d tipo=%r quantidade=%d origem=%r",
            figurinha_id,
            tipo,
            quantidade,
            origem,
        )
        return self._repo.insert(
            figurinha_id=figurinha_id,
            tipo=tipo,
            quantidade=quantidade,
            entrada_bruta=entrada_bruta,
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            origem=origem,
            observacao=observacao,
        )
