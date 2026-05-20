"""Domain model for a stock movement (movimentacao) in the Copa 2026 album bot.

This module defines the :class:`Movimentacao` dataclass which mirrors the
``movimentacoes`` database table.  It contains no business logic — it is a
pure data container used to carry typed records across application layers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Movimentacao:
    """Represents a single row in the ``movimentacoes`` table.

    Attributes:
        id: Auto-incremented primary key.
        figurinha_id: Foreign key referencing ``figurinhas.id``.
        tipo: Movement direction — ``"ENTRADA"`` (stock in) or
            ``"SAIDA"`` (stock out).
        quantidade: Number of stickers moved (always positive).
        origem: Source of the movement — ``"MANUAL"`` or ``"TROCA"``.
        observacao: Free-text note attached to the movement (optional).
        telegram_user_id: Numeric Telegram user ID that triggered the
            movement (optional).
        telegram_username: Telegram ``@username`` of the user (optional).
        entrada_bruta: Raw text input received from the Telegram message
            (optional), stored for audit / debugging purposes.
        created_at: Timestamp of row creation (UTC-aware).
    """

    id: int
    figurinha_id: int
    tipo: str
    quantidade: int
    origem: str
    observacao: Optional[str]
    telegram_user_id: Optional[int]
    telegram_username: Optional[str]
    entrada_bruta: Optional[str]
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple) -> "Movimentacao":
        """Construct a :class:`Movimentacao` from a raw database row.

        The column order must match the SELECT order used in repository
        queries::

            id, figurinha_id, tipo, quantidade, origem, observacao,
            telegram_user_id, telegram_username, entrada_bruta, created_at

        Args:
            row: A tuple with exactly 10 elements as returned by psycopg2.

        Returns:
            A fully populated :class:`Movimentacao` instance.

        Raises:
            ValueError: If *row* does not contain the expected number of
                elements.
        """
        _EXPECTED_COLUMNS = 10
        if len(row) != _EXPECTED_COLUMNS:
            raise ValueError(
                f"Movimentacao.from_row expects {_EXPECTED_COLUMNS} columns, "
                f"got {len(row)}: {row!r}"
            )
        return cls(
            id=row[0],
            figurinha_id=row[1],
            tipo=row[2],
            quantidade=row[3],
            origem=row[4],
            observacao=row[5],
            telegram_user_id=row[6],
            telegram_username=row[7],
            entrada_bruta=row[8],
            created_at=row[9],
        )
