"""Domain model for a sticker (figurinha) in the Copa 2026 album.

This module defines the :class:`Figurinha` dataclass which mirrors the
``figurinhas`` database table.  It contains no business logic — it is a
pure data container used to carry typed records across application layers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Figurinha:
    """Represents a single sticker entry in the ``figurinhas`` table.

    Attributes:
        id: Auto-incremented primary key.
        grupo: Album group label (e.g. ``"A"``, ``"FWC"``, ``"CC"``).
        codigo_selecao: Short team / section code (e.g. ``"BRA"``, ``"FWC"``).
        nome_selecao: Full team / section name in Portuguese.
        numero: Sticker number within the team / section.
        codigo_figurinha: Unique sticker code in ``<code>-<number>`` format
            (e.g. ``"BRA-1"``, ``"FWC-0"``).
        quantidade: Current quantity owned by the user.
        created_at: Timestamp of row creation (UTC-aware).
        updated_at: Timestamp of the last row update (UTC-aware).
    """

    id: int
    grupo: str
    codigo_selecao: str
    nome_selecao: str
    numero: int
    codigo_figurinha: str
    quantidade: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: tuple) -> "Figurinha":
        """Construct a :class:`Figurinha` from a raw database row.

        The column order must match the SELECT order used in repository
        queries::

            id, grupo, codigo_selecao, nome_selecao, numero,
            codigo_figurinha, quantidade, created_at, updated_at

        Args:
            row: A tuple with exactly 9 elements as returned by psycopg2.

        Returns:
            A fully populated :class:`Figurinha` instance.

        Raises:
            ValueError: If *row* does not contain the expected number of
                elements.
        """
        _EXPECTED_COLUMNS = 9
        if len(row) != _EXPECTED_COLUMNS:
            raise ValueError(
                f"Figurinha.from_row expects {_EXPECTED_COLUMNS} columns, "
                f"got {len(row)}: {row!r}"
            )
        return cls(
            id=row[0],
            grupo=row[1],
            codigo_selecao=row[2],
            nome_selecao=row[3],
            numero=row[4],
            codigo_figurinha=row[5],
            quantidade=row[6],
            created_at=row[7],
            updated_at=row[8],
        )
