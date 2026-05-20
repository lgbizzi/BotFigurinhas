"""Service layer for read-only album query operations.

Agent: Backend Dev

:class:`AlbumQueryService` provides high-level query operations over the
album data: grouped missing stickers, repeated stickers, and overall
completion progress.  It delegates all persistence to the injected
:class:`~repositories.figurinha_repository.FigurinhaRepository`.
"""

import logging

from models.figurinha import Figurinha
from models.progresso import Progresso
from repositories.figurinha_repository import FigurinhaRepository

logger = logging.getLogger(__name__)


class AlbumQueryService:
    """Read-only service for album completion queries.

    Provides higher-level grouping and aggregation over raw repository
    results.  All write operations remain in
    :class:`~services.figurinha_service.FigurinhaService`.

    Args:
        figurinha_repository: Injected repository handling DB queries.
    """

    def __init__(self, figurinha_repository: FigurinhaRepository) -> None:
        """Initialise the service with an injected repository.

        Args:
            figurinha_repository: Concrete or mock repository instance.
        """
        self._repo = figurinha_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def faltantes_agrupados(
        self, telegram_user_id: int
    ) -> dict[str, dict[str, list[Figurinha]]]:
        """Return missing stickers grouped by album group and selection name.

        Calls :meth:`~repositories.figurinha_repository.FigurinhaRepository.find_faltantes`
        and organises the result into a nested dict keyed first by
        ``grupo`` then by ``nome_selecao``.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            Nested dict ``{grupo: {nome_selecao: [Figurinha, ...]}}`` for
            every figurinha with ``quantidade == 0``.  Returns an empty
            dict when the album is complete.
        """
        faltantes = self._repo.find_faltantes(telegram_user_id)
        logger.debug("faltantes_agrupados: processing %d faltantes", len(faltantes))
        return self._agrupar(faltantes)

    def repetidas(self, telegram_user_id: int) -> list[Figurinha]:
        """Return all stickers the user owns more than one copy of.

        Delegates directly to
        :meth:`~repositories.figurinha_repository.FigurinhaRepository.find_repetidas`.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of :class:`~models.figurinha.Figurinha` with ``quantidade > 1``.
        """
        return self._repo.find_repetidas(telegram_user_id)

    def progresso(self, telegram_user_id: int) -> Progresso:
        """Return aggregated album completion statistics.

        Delegates directly to
        :meth:`~repositories.figurinha_repository.FigurinhaRepository.get_progresso`.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            A :class:`~models.progresso.Progresso` frozen dataclass.
        """
        return self._repo.get_progresso(telegram_user_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _agrupar(figurinhas: list[Figurinha]) -> dict[str, dict[str, list[Figurinha]]]:
        """Group a list of figurinhas into a nested dict by grupo and nome_selecao.

        Args:
            figurinhas: Flat list of :class:`~models.figurinha.Figurinha` objects.

        Returns:
            Nested dict ``{grupo: {nome_selecao: [Figurinha, ...]}}``.
        """
        resultado: dict[str, dict[str, list[Figurinha]]] = {}
        for fig in figurinhas:
            resultado.setdefault(fig.grupo, {}).setdefault(fig.nome_selecao, []).append(fig)
        return resultado
