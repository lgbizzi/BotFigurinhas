"""Domain model for album completion progress.

Agent: Backend Dev

This module defines the :class:`Progresso` frozen dataclass which aggregates
sticker ownership statistics for a user's album.  It contains no persistence
logic — it is a pure value object produced by the repository layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Progresso:
    """Aggregated album completion statistics.

    Attributes:
        total_album: Total number of distinct sticker types in the album.
        tipos_possuidos: Count of sticker types where ``quantidade > 0``.
        total_exemplares: Sum of all ``quantidade`` values across the album.
        paises_completos: Number of group A–L selections where every sticker
            has ``quantidade > 0``.
        top3_proximos: Up to 3 tuples ``(nome_selecao, qtd_faltantes)`` for
            group A–L selections closest to completion, ordered ascending by
            missing sticker count.
        top3_distantes: Up to 3 tuples ``(nome_selecao, qtd_faltantes)`` for
            group A–L selections farthest from completion, ordered descending
            by missing sticker count.
        brilhantes_faltantes: Canonical codes of stickers that are "brilhantes"
            (numero=1 of any A–L selection, or any FWC sticker) and are still
            missing (``quantidade = 0``).
        cc_faltantes: Canonical codes of CC stickers with ``quantidade = 0``,
            ordered by ``numero``.
    """

    total_album: int
    tipos_possuidos: int
    total_exemplares: int
    paises_completos: int = 0
    top3_proximos: tuple[tuple[str, int], ...] = ()
    top3_distantes: tuple[tuple[str, int], ...] = ()
    brilhantes_faltantes: tuple[str, ...] = ()
    cc_faltantes: tuple[str, ...] = ()

    @property
    def tipos_faltantes(self) -> int:
        """Number of sticker types the user still needs.

        Returns:
            Difference between total types in the album and types owned.
        """
        return self.total_album - self.tipos_possuidos

    @property
    def percentual(self) -> float:
        """Album completion percentage rounded to one decimal place.

        Returns:
            Completion percentage between 0.0 and 100.0; returns 0.0 when
            ``total_album`` is zero to avoid division by zero.
        """
        if self.total_album == 0:
            return 0.0
        return round(self.tipos_possuidos / self.total_album * 100, 1)
