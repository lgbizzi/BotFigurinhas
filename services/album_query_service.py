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
    ) -> list[tuple[str, list[tuple[str, str, list[Figurinha]]]]]:
        """Return missing stickers grouped by album group in physical page order.

        Produces one message-group per album group (A–L, FWC, CC).  FWC stickers
        whose ``pagina >= 100`` appear as a separate group from early FWC stickers
        (``pagina <= 3``), so they show at the correct position near the end of
        the album instead of at the beginning.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of ``(group_header, [(nome_selecao, codigo_selecao, figurinhas)])``
            tuples ordered by the first ``pagina`` seen in each group.  Returns an
            empty list when the album is complete.
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

    def repetidas_agrupadas(
        self, telegram_user_id: int
    ) -> list[tuple[str, list[tuple[str, str, list[Figurinha]]]]]:
        """Return repeated stickers grouped by album group in physical page order.

        Applies the same grouping logic as :meth:`faltantes_agrupados`.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of ``(group_header, [(nome_selecao, codigo_selecao, figurinhas)])``
            tuples ordered by ascending page.  Returns an empty list when the
            user has no repeated stickers.
        """
        repetidas = self._repo.find_repetidas(telegram_user_id)
        logger.debug("repetidas_agrupadas: processing %d repetidas", len(repetidas))
        return self._agrupar(repetidas)

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

    def progresso_detalhado(self, telegram_user_id: int) -> Progresso:
        """Return full album completion statistics including detailed breakdowns.

        Aggregates results from repository queries into a single enriched
        :class:`~models.progresso.Progresso` value object.  The "brilhante",
        "top-3", and "países completos" filtering rules are applied here
        (service layer), not in the repository.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping all queries.

        Returns:
            A :class:`~models.progresso.Progresso` frozen dataclass with all
            fields populated.
        """
        base = self._repo.get_progresso(telegram_user_id)
        contagem = self._repo.get_selecoes_faltantes_contagem(telegram_user_id)
        faltantes = self._repo.find_faltantes(telegram_user_id)
        cc = self._repo.get_cc_faltantes(telegram_user_id)
        paises = self._paises_completos(contagem)
        top3_prox = self._top3_proximos(contagem)
        top3_dist = self._top3_distantes(contagem)
        brilhantes = self._extrair_brilhantes(faltantes)
        logger.debug("progresso_detalhado: user=%d paises_completos=%d", telegram_user_id, paises)
        return self._build_progresso_detalhado(base, paises, top3_prox, top3_dist, brilhantes, cc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _paises_completos(contagem: list[tuple[str, int]]) -> int:
        """Count A–L selections where every sticker is owned (qtd_faltantes == 0).

        A selection is complete when the repository reports zero faltantes for
        it.  This business rule lives in the service, not in the repository SQL.

        Args:
            contagem: All A–L selections with their faltantes count.

        Returns:
            Number of selections with zero missing stickers.
        """
        return sum(1 for _, f in contagem if f == 0)

    @staticmethod
    def _top3_proximos(contagem: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """Return top-3 selections closest to completion (fewest faltantes > 0).

        Args:
            contagem: All A–L selections with their faltantes count, ASC ordered.

        Returns:
            Up to 3 tuples ``(nome_selecao, qtd_faltantes)`` for incomplete
            selections, ordered ascending by missing count.
        """
        return [(n, f) for n, f in contagem if f > 0][:3]

    @staticmethod
    def _top3_distantes(contagem: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """Return top-3 selections farthest from completion (most faltantes > 0).

        Args:
            contagem: All A–L selections with their faltantes count, ASC ordered.

        Returns:
            Up to 3 tuples ``(nome_selecao, qtd_faltantes)`` for incomplete
            selections, ordered descending by missing count.
        """
        incompletas = [(n, f) for n, f in contagem if f > 0]
        return sorted(incompletas, key=lambda x: x[1], reverse=True)[:3]

    @staticmethod
    def _extrair_brilhantes(faltantes: list) -> list[str]:
        """Extract brilhante codes from the full list of missing stickers.

        A "brilhante" is sticker ``numero=1`` of any A–L selection, or any
        FWC sticker.  This business rule lives in the service, not the
        repository.

        Args:
            faltantes: All missing :class:`~models.figurinha.Figurinha` objects.

        Returns:
            List of ``codigo_figurinha`` strings for brilhantes, in the same
            order as the input list.
        """
        return [
            f.codigo_figurinha for f in faltantes
            if (f.numero == 1 and f.grupo not in ("FWC", "CC"))
            or f.codigo_selecao == "FWC"
        ]

    @staticmethod
    def _build_progresso_detalhado(
        base: Progresso,
        paises: int,
        prox: list[tuple[str, int]],
        dist: list[tuple[str, int]],
        brilhantes: list[str],
        cc: list[str],
    ) -> Progresso:
        """Construct an enriched :class:`Progresso` from component query results.

        Args:
            base: Base progress object with total_album, tipos_possuidos, total_exemplares.
            paises: Count of fully-complete A–L selections.
            prox: Up to 3 closest-to-completion ``(nome_selecao, faltantes)`` pairs.
            dist: Up to 3 farthest-from-completion ``(nome_selecao, faltantes)`` pairs.
            brilhantes: Codes of missing brilhante stickers.
            cc: Codes of missing CC stickers.

        Returns:
            A fully-populated :class:`~models.progresso.Progresso` frozen dataclass.
        """
        return Progresso(
            total_album=base.total_album,
            tipos_possuidos=base.tipos_possuidos,
            total_exemplares=base.total_exemplares,
            paises_completos=paises,
            top3_proximos=tuple(tuple(t) for t in prox),  # type: ignore[misc]
            top3_distantes=tuple(tuple(t) for t in dist),  # type: ignore[misc]
            brilhantes_faltantes=tuple(brilhantes),
            cc_faltantes=tuple(cc),
        )

    @staticmethod
    def _compute_header(grupo: str) -> str:
        """Return the display header for an album group.

        Args:
            grupo: Album group code (e.g. ``"A"``, ``"FWC"``, ``"CC"``).

        Returns:
            ``"Grupo A"`` for letter groups; bare group code for specials.
        """
        if grupo in ("FWC", "CC"):
            return grupo
        return f"Grupo {grupo}"

    @staticmethod
    def _flush_grupo(
        result: list,
        key: tuple[str, bool],
        countries: dict[str, tuple[str, list[Figurinha]]],
    ) -> None:
        """Append a completed group entry to result.

        Args:
            result: Accumulated output list to append to.
            key: ``(grupo, is_late)`` pair identifying the group being flushed.
            countries: Mapping ``nome_selecao → (codigo_selecao, figurinhas)``
                accumulated for the group.
        """
        header = AlbumQueryService._compute_header(key[0])
        secoes = [(n, c, figs) for n, (c, figs) in countries.items()]
        result.append((header, secoes))

    @staticmethod
    def _agrupar(
        figurinhas: list[Figurinha],
    ) -> list[tuple[str, list[tuple[str, str, list[Figurinha]]]]]:
        """Group figurinhas by album group in physical page order.

        Each album group (A–L, FWC early, FWC late, CC) becomes one outer
        entry.  Within each group, stickers are sub-grouped by country.

        FWC stickers whose ``pagina >= 100`` form a separate group entry from
        early FWC stickers (``pagina <= 3``).

        Args:
            figurinhas: Flat list sorted by ``pagina`` then ``numero``.

        Returns:
            List of ``(group_header, [(nome_selecao, codigo_selecao, figs)])``
            tuples in ascending page order.
        """
        result: list[tuple[str, list[tuple[str, str, list[Figurinha]]]]] = []
        current_key: tuple[str, bool] | None = None
        current_countries: dict[str, tuple[str, list[Figurinha]]] = {}
        for fig in figurinhas:
            is_late = fig.codigo_selecao == "FWC" and fig.pagina >= 100
            key = (fig.grupo, is_late)
            if key != current_key:
                if current_key is not None:
                    AlbumQueryService._flush_grupo(result, current_key, current_countries)
                current_key = key
                current_countries = {}
            nome = fig.nome_selecao
            if nome not in current_countries:
                current_countries[nome] = (fig.codigo_selecao, [])
            current_countries[nome][1].append(fig)
        if current_key is not None and current_countries:
            AlbumQueryService._flush_grupo(result, current_key, current_countries)
        return result
