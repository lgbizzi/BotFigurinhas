"""Repository for the ``figurinhas`` table.

Agent: Backend Dev

Encapsulates all SQL operations for :class:`models.figurinha.Figurinha` rows.
No SQL may appear outside this module for this entity.
"""

import logging
from typing import Optional

import psycopg2
import psycopg2.extensions

from models.figurinha import Figurinha
from models.progresso import Progresso
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column list shared by all SELECT queries — must match Figurinha.from_row()
# ---------------------------------------------------------------------------
_SELECT_COLS = (
    "id, grupo, codigo_selecao, nome_selecao, numero, "
    "codigo_figurinha, quantidade, created_at, updated_at"
)


class FigurinhaRepository(BaseRepository):
    """Persistence layer for the ``figurinhas`` table.

    All write operations are wrapped in explicit transactions with rollback on
    failure.  ``SELECT … FOR UPDATE`` is used in read-before-write queries to
    prevent race conditions under concurrent access.

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
    # Queries
    # ------------------------------------------------------------------

    def find_by_codigo(
        self, codigo_figurinha: str, telegram_user_id: int
    ) -> Optional[Figurinha]:
        """Fetch a figurinha by its canonical code, locking the row for update.

        Uses ``SELECT … FOR UPDATE`` so that callers that subsequently call
        :meth:`update_quantidade` on the returned object operate on a locked
        row, preventing lost-update race conditions.

        Args:
            codigo_figurinha: Canonical sticker code, e.g. ``"BRA-1"``.
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            A :class:`Figurinha` instance if found, ``None`` otherwise.
        """
        sql = (
            f"SELECT {_SELECT_COLS} "
            "FROM figurinhas "
            "WHERE codigo_figurinha = %s AND telegram_user_id = %s "
            "FOR UPDATE"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (codigo_figurinha, telegram_user_id))
            row = cur.fetchone()

        if row is None:
            logger.debug("find_by_codigo: code=%r user=%d not found", codigo_figurinha, telegram_user_id)
            return None

        figurinha = Figurinha.from_row(row)
        logger.debug("find_by_codigo: found figurinha id=%d code=%r", figurinha.id, codigo_figurinha)
        return figurinha

    def find_by_par(
        self, *, codigo_selecao: str, numero: int, telegram_user_id: int
    ) -> Optional[Figurinha]:
        """Fetch a figurinha by the (codigo_selecao, numero) pair, locking the row.

        Uses ``SELECT … FOR UPDATE`` for the same concurrency guarantees as
        :meth:`find_by_codigo`.

        Args:
            codigo_selecao: Short team/section code, e.g. ``"BRA"``.
            numero: Sticker number within the team/section.
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            A :class:`Figurinha` instance if found, ``None`` otherwise.
        """
        sql = (
            f"SELECT {_SELECT_COLS} "
            "FROM figurinhas "
            "WHERE codigo_selecao = %s AND numero = %s AND telegram_user_id = %s "
            "FOR UPDATE"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (codigo_selecao, numero, telegram_user_id))
            row = cur.fetchone()

        if row is None:
            logger.debug(
                "find_by_par: selecao=%r numero=%d user=%d not found",
                codigo_selecao,
                numero,
                telegram_user_id,
            )
            return None

        figurinha = Figurinha.from_row(row)
        logger.debug(
            "find_by_par: found figurinha id=%d selecao=%r numero=%d",
            figurinha.id,
            codigo_selecao,
            numero,
        )
        return figurinha

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def update_quantidade(
        self, *, figurinha_id: int, quantidade: int, telegram_user_id: int
    ) -> None:
        """Persist a new quantity for the given figurinha.

        The database CHECK constraint (``quantidade >= 0``) is the authoritative
        guard against negative stock — this method intentionally lets the
        constraint propagate as a :class:`psycopg2.DatabaseError` so that the
        caller can decide how to handle it.

        Args:
            figurinha_id: Primary key of the row to update.
            quantidade: New quantity value (must satisfy the DB CHECK constraint).
            telegram_user_id: Numeric Telegram user ID scoping the update.

        Raises:
            psycopg2.DatabaseError: If the database rejects the update (e.g.
                CHECK constraint violation).
        """
        sql = (
            "UPDATE figurinhas "
            "SET quantidade = %s, updated_at = NOW() "
            "WHERE id = %s AND telegram_user_id = %s"
        )
        try:
            with self._conn.cursor() as cur:
                cur.execute(sql, (quantidade, figurinha_id, telegram_user_id))
            logger.debug(
                "update_quantidade: figurinha_id=%d new_quantidade=%d user=%d",
                figurinha_id,
                quantidade,
                telegram_user_id,
            )
        except psycopg2.DatabaseError:
            self._conn.rollback()
            logger.exception(
                "update_quantidade: rollback after error — figurinha_id=%d quantidade=%d",
                figurinha_id,
                quantidade,
            )
            raise

    # ------------------------------------------------------------------
    # Read-only queries
    # ------------------------------------------------------------------

    def find_faltantes(self, telegram_user_id: int) -> list[Figurinha]:
        """Fetch all figurinhas the user still needs (quantidade = 0).

        Results are ordered by ``grupo``, ``codigo_selecao``, and ``numero``
        so that callers receive them in album order.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of :class:`Figurinha` instances with ``quantidade == 0``.
        """
        sql = (
            f"SELECT {_SELECT_COLS} FROM figurinhas "
            "WHERE quantidade = 0 AND telegram_user_id = %s "
            "ORDER BY grupo, codigo_selecao, numero"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            rows = cur.fetchall()

        figurinhas = [Figurinha.from_row(row) for row in rows]
        logger.debug("find_faltantes: returned %d rows user=%d", len(figurinhas), telegram_user_id)
        return figurinhas

    def find_repetidas(self, telegram_user_id: int) -> list[Figurinha]:
        """Fetch all figurinhas the user owns more than one copy of (quantidade > 1).

        Results are ordered by ``codigo_selecao`` and ``numero``.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of :class:`Figurinha` instances with ``quantidade > 1``.
        """
        sql = (
            f"SELECT {_SELECT_COLS} FROM figurinhas "
            "WHERE quantidade > 1 AND telegram_user_id = %s "
            "ORDER BY codigo_selecao, numero"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            rows = cur.fetchall()

        figurinhas = [Figurinha.from_row(row) for row in rows]
        logger.debug("find_repetidas: returned %d rows user=%d", len(figurinhas), telegram_user_id)
        return figurinhas

    def get_progresso(self, telegram_user_id: int) -> Progresso:
        """Return aggregated album completion statistics for a single user.

        Executes a single aggregate query to count total sticker types,
        types owned (``quantidade > 0``), and total exemplar count.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            A :class:`~models.progresso.Progresso` frozen dataclass.
        """
        sql = (
            "SELECT COUNT(*), "
            "COUNT(*) FILTER (WHERE quantidade > 0), "
            "COALESCE(SUM(quantidade), 0) "
            "FROM figurinhas "
            "WHERE telegram_user_id = %s"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            row = cur.fetchone()

        total_album, tipos_possuidos, total_exemplares = row  # type: ignore[misc]
        progresso = Progresso(
            total_album=int(total_album),
            tipos_possuidos=int(tipos_possuidos),
            total_exemplares=int(total_exemplares),
        )
        logger.debug(
            "get_progresso: total=%d possuidos=%d exemplares=%d user=%d",
            progresso.total_album,
            progresso.tipos_possuidos,
            progresso.total_exemplares,
            telegram_user_id,
        )
        return progresso

    # ------------------------------------------------------------------
    # Per-user album initialisation
    # ------------------------------------------------------------------

    def usuario_tem_album(self, telegram_user_id: int) -> bool:
        """Check whether a user already has sticker rows in the database.

        Args:
            telegram_user_id: Numeric Telegram user ID to check.

        Returns:
            ``True`` if at least one row exists for the user, ``False`` otherwise.
        """
        sql = "SELECT EXISTS (SELECT 1 FROM figurinhas WHERE telegram_user_id = %s LIMIT 1)"
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            row = cur.fetchone()
        result: bool = bool(row[0]) if row else False
        logger.debug("usuario_tem_album: user=%d exists=%s", telegram_user_id, result)
        return result

    def inicializar_album(self, telegram_user_id: int, stickers: list[dict]) -> None:
        """Batch-insert all sticker rows for a new user with quantidade=0.

        Args:
            telegram_user_id: Numeric Telegram user ID owning the new rows.
            stickers: List of dicts with keys: ``grupo``, ``codigo_selecao``,
                ``nome_selecao``, ``numero``, ``codigo_figurinha``.
        """
        sql = (
            "INSERT INTO figurinhas "
            "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, codigo_figurinha, quantidade) "
            "VALUES (%s, %s, %s, %s, %s, %s, 0) "
            "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING"
        )
        rows = [
            (
                telegram_user_id,
                s["grupo"],
                s["codigo_selecao"],
                s["nome_selecao"],
                s["numero"],
                s["codigo_figurinha"],
            )
            for s in stickers
        ]
        with self._conn.cursor() as cur:
            cur.executemany(sql, rows)
        logger.debug("inicializar_album: inserted %d stickers for user=%d", len(rows), telegram_user_id)
