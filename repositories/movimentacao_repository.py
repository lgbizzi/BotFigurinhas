"""Repository for the ``movimentacoes`` table.

Encapsulates all SQL operations for :class:`models.movimentacao.Movimentacao`
rows.  No SQL may appear outside this module for this entity.
"""

import logging
from typing import Optional

import psycopg2
import psycopg2.extensions

from models.movimentacao import Movimentacao
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

_INSERT_SQL = """
    INSERT INTO movimentacoes (
        figurinha_id,
        tipo,
        quantidade,
        origem,
        observacao,
        telegram_user_id,
        telegram_username,
        entrada_bruta
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s
    )
    RETURNING id, created_at
"""


class MovimentacaoRepository(BaseRepository):
    """Persistence layer for the ``movimentacoes`` table.

    All write operations are wrapped in explicit transactions with rollback on
    failure.  The ``INSERT … RETURNING`` pattern is used to retrieve
    database-generated values (``id``, ``created_at``) without a subsequent
    SELECT round-trip.

    Args:
        connection: An open psycopg2 connection injected by the caller.
    """

    def __init__(self, connection: psycopg2.extensions.connection) -> None:
        """Initialise the repository with an injected database connection.

        Args:
            connection: Open psycopg2 connection.  The repository does not
                manage the connection lifecycle.
        """
        super().__init__(connection)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_params(
        self,
        figurinha_id: int,
        tipo: str,
        quantidade: int,
        origem: str,
        observacao: Optional[str],
        telegram_user_id: Optional[int],
        telegram_username: Optional[str],
        entrada_bruta: Optional[str],
    ) -> tuple:
        """Build the positional parameters tuple for :data:`_INSERT_SQL`.

        Args:
            figurinha_id: Foreign key referencing ``figurinhas.id``.
            tipo: Movement direction — ``"ENTRADA"`` or ``"SAIDA"``.
            quantidade: Number of stickers moved.
            origem: Source of the movement.
            observacao: Optional free-text note.
            telegram_user_id: Numeric Telegram user ID (optional).
            telegram_username: Telegram ``@username`` (optional).
            entrada_bruta: Raw text input as received from Telegram (optional).

        Returns:
            Tuple of values ordered to match the ``INSERT`` column list in
            :data:`_INSERT_SQL`.
        """
        return (figurinha_id, tipo, quantidade, origem, observacao, telegram_user_id, telegram_username, entrada_bruta)

    def _build_movimentacao(self, returning: tuple, params: tuple) -> Movimentacao:
        """Construct a :class:`Movimentacao` from ``RETURNING`` data and insert params.

        Args:
            returning: Two-element tuple ``(id, created_at)`` from the database.
            params: The same positional tuple passed to :data:`_INSERT_SQL`.

        Returns:
            Fully populated :class:`Movimentacao` instance.
        """
        generated_id, generated_created_at = returning[0], returning[1]
        figurinha_id, tipo, quantidade, origem, observacao, telegram_user_id, telegram_username, entrada_bruta = params
        logger.debug(
            "insert: persisted movimentacao id=%d figurinha_id=%d tipo=%r quantidade=%d",
            generated_id, figurinha_id, tipo, quantidade,
        )
        return Movimentacao(
            id=generated_id, figurinha_id=figurinha_id, tipo=tipo, quantidade=quantidade,
            origem=origem, observacao=observacao, telegram_user_id=telegram_user_id,
            telegram_username=telegram_username, entrada_bruta=entrada_bruta,
            created_at=generated_created_at,
        )

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def insert(
        self,
        *,
        figurinha_id: int,
        tipo: str,
        quantidade: int,
        origem: str = "MANUAL",
        observacao: Optional[str] = None,
        telegram_user_id: Optional[int] = None,
        telegram_username: Optional[str] = None,
        entrada_bruta: Optional[str] = None,
    ) -> Movimentacao:
        """Persist a new movement record and return it with DB-generated fields.

        The ``id`` and ``created_at`` fields of the returned object are filled
        in by the database via ``RETURNING id, created_at``.

        The transaction is rolled back automatically on any database error so
        that the connection remains usable after the exception is re-raised.

        .. note::
            **Commit is the caller's responsibility.**  This method executes
            the ``INSERT`` but never calls ``connection.commit()``.  The caller
            must commit (or roll back) the transaction after all related
            operations in the same unit of work have succeeded.

        Args:
            figurinha_id: Foreign key referencing ``figurinhas.id``.
            tipo: Movement direction — ``"ENTRADA"`` or ``"SAIDA"``.
            quantidade: Number of stickers moved.  Must satisfy the DB CHECK
                constraint (``quantidade > 0``).
            origem: Source of the movement — ``"MANUAL"`` (default) or
                ``"TROCA"``.
            observacao: Optional free-text note.
            telegram_user_id: Numeric Telegram user ID (optional).
            telegram_username: Telegram ``@username`` (optional).
            entrada_bruta: Raw text input as received from Telegram (optional).
                Stored verbatim — no normalisation is applied.

        Returns:
            A fully populated :class:`Movimentacao` instance, including the
            ``id`` and ``created_at`` assigned by the database.

        Raises:
            psycopg2.DatabaseError: If the database rejects the insert (e.g.
                FK violation or CHECK constraint failure).
            RuntimeError: If ``INSERT RETURNING`` yields no row, which would
                indicate an unexpected engine-level anomaly.
        """
        params = self._build_params(
            figurinha_id, tipo, quantidade, origem,
            observacao, telegram_user_id, telegram_username, entrada_bruta,
        )

        try:
            with self._conn.cursor() as cur:
                cur.execute(_INSERT_SQL, params)
                returning = cur.fetchone()
        except psycopg2.DatabaseError:
            self._conn.rollback()
            logger.exception(
                "insert: rollback after error — figurinha_id=%d tipo=%r quantidade=%d",
                figurinha_id, tipo, quantidade,
            )
            raise

        if returning is None:
            raise RuntimeError("INSERT RETURNING retornou resultado vazio — inesperado.")

        return self._build_movimentacao(returning, params)
