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
    "codigo_figurinha, quantidade, pagina, created_at, updated_at"
)

_SQL_INIT_ALBUM = (
    "INSERT INTO figurinhas "
    "(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, codigo_figurinha, quantidade, pagina) "
    "VALUES (%s, %s, %s, %s, %s, %s, 0, %s) "
    "ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING"
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
            logger.debug("find_by_par: selecao=%r numero=%d user=%d not found", codigo_selecao, numero, telegram_user_id)
            return None

        figurinha = Figurinha.from_row(row)
        logger.debug("find_by_par: found id=%d selecao=%r numero=%d", figurinha.id, codigo_selecao, numero)
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
            logger.debug("update_quantidade: id=%d new_qtd=%d user=%d", figurinha_id, quantidade, telegram_user_id)
        except psycopg2.DatabaseError:
            self._conn.rollback()
            logger.exception("update_quantidade: rollback — id=%d qtd=%d", figurinha_id, quantidade)
            raise

    # ------------------------------------------------------------------
    # Read-only queries
    # ------------------------------------------------------------------

    def find_by_codigo_readonly(
        self, codigo_figurinha: str, telegram_user_id: int
    ) -> Optional[Figurinha]:
        """Fetch a figurinha by canonical code without locking the row.

        For read-only queries only.  Use :meth:`find_by_codigo` when the
        caller will subsequently call :meth:`update_quantidade`.

        Args:
            codigo_figurinha: Canonical sticker code, e.g. ``"BRA-1"``.
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            A :class:`Figurinha` instance if found, ``None`` otherwise.
        """
        sql = (
            f"SELECT {_SELECT_COLS} "
            "FROM figurinhas "
            "WHERE codigo_figurinha = %s AND telegram_user_id = %s"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (codigo_figurinha, telegram_user_id))
            row = cur.fetchone()

        if row is None:
            logger.debug("find_by_codigo_readonly: code=%r user=%d not found", codigo_figurinha, telegram_user_id)
            return None

        figurinha = Figurinha.from_row(row)
        logger.debug("find_by_codigo_readonly: found id=%d code=%r", figurinha.id, codigo_figurinha)
        return figurinha

    def find_by_selecao(
        self, codigo_selecao: str, telegram_user_id: int
    ) -> list[Figurinha]:
        """Return all figurinhas for a given selection, ordered by numero.

        Args:
            codigo_selecao: Short team/section code, e.g. ``"BRA"``.
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of :class:`Figurinha` instances ordered by ``numero`` ascending.
        """
        sql = (
            f"SELECT {_SELECT_COLS} "
            "FROM figurinhas "
            "WHERE codigo_selecao = %s AND telegram_user_id = %s "
            "ORDER BY numero"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (codigo_selecao, telegram_user_id))
            rows = cur.fetchall()

        figurinhas = [Figurinha.from_row(row) for row in rows]
        logger.debug("find_by_selecao: selecao=%r returned %d rows user=%d", codigo_selecao, len(figurinhas), telegram_user_id)
        return figurinhas

    def find_faltantes(self, telegram_user_id: int) -> list[Figurinha]:
        """Fetch all figurinhas the user still needs (quantidade = 0).

        Results are ordered by ``pagina`` and ``numero`` so that callers
        receive them in physical album page order.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of :class:`Figurinha` instances with ``quantidade == 0``.
        """
        sql = (
            f"SELECT {_SELECT_COLS} FROM figurinhas "
            "WHERE quantidade = 0 AND telegram_user_id = %s "
            "ORDER BY pagina, numero"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            rows = cur.fetchall()

        figurinhas = [Figurinha.from_row(row) for row in rows]
        logger.debug("find_faltantes: returned %d rows user=%d", len(figurinhas), telegram_user_id)
        return figurinhas

    def find_repetidas(self, telegram_user_id: int) -> list[Figurinha]:
        """Fetch all figurinhas the user owns more than one copy of (quantidade > 1).

        Results are ordered by ``pagina`` and ``numero`` so that callers
        receive them in physical album page order.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of :class:`Figurinha` instances with ``quantidade > 1``.
        """
        sql = (
            f"SELECT {_SELECT_COLS} FROM figurinhas "
            "WHERE quantidade > 1 AND telegram_user_id = %s "
            "ORDER BY pagina, numero"
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

        progresso = self._build_progresso(row)  # type: ignore[arg-type]
        logger.debug("get_progresso: total=%d possuidos=%d user=%d", progresso.total_album, progresso.tipos_possuidos, telegram_user_id)
        return progresso

    def get_selecoes_faltantes_contagem(self, telegram_user_id: int) -> list[tuple[str, int]]:
        """Return faltantes count per A–L selection, ordered ascending by faltantes.

        Returns all selections regardless of completion state.  The caller is
        responsible for filtering incomplete selections and limiting the result.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of ``(nome_selecao, qtd_faltantes)`` tuples for every A–L
            selection, ordered by ``faltantes ASC``.
        """
        sql = (
            "SELECT nome_selecao, COUNT(*) FILTER (WHERE quantidade = 0) AS faltantes "
            "FROM figurinhas "
            "WHERE telegram_user_id = %s AND grupo NOT IN ('FWC', 'CC') "
            "GROUP BY codigo_selecao, nome_selecao "
            "ORDER BY faltantes ASC"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            rows = cur.fetchall()
        result = [(str(r[0]), int(r[1])) for r in rows]
        logger.debug("get_selecoes_faltantes_contagem: %d entries user=%d", len(result), telegram_user_id)
        return result

    def get_cc_faltantes(self, telegram_user_id: int) -> list[str]:
        """Return codes of missing CC stickers for a user.

        Only rows with ``codigo_selecao = 'CC'`` and ``quantidade = 0`` are
        returned, ordered by ``numero`` ascending.

        Args:
            telegram_user_id: Numeric Telegram user ID scoping the query.

        Returns:
            List of ``codigo_figurinha`` strings.
        """
        sql = (
            "SELECT codigo_figurinha "
            "FROM figurinhas "
            "WHERE telegram_user_id = %s AND codigo_selecao = 'CC' AND quantidade = 0 "
            "ORDER BY numero"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, (telegram_user_id,))
            rows = cur.fetchall()
        result = [str(r[0]) for r in rows]
        logger.debug("get_cc_faltantes: returned %d entries user=%d", len(result), telegram_user_id)
        return result

    @staticmethod
    def _build_progresso(row: tuple) -> Progresso:
        """Construct a :class:`~models.progresso.Progresso` from an aggregate query row.

        Args:
            row: Three-element tuple ``(total_album, tipos_possuidos, total_exemplares)``
                as returned by the ``get_progresso`` SQL query.

        Returns:
            A frozen :class:`~models.progresso.Progresso` dataclass instance.
        """
        total_album, tipos_possuidos, total_exemplares = row
        return Progresso(
            total_album=int(total_album),
            tipos_possuidos=int(tipos_possuidos),
            total_exemplares=int(total_exemplares),
        )

    def get_dados_usuario(self, telegram_user_id: int) -> dict:
        """Return a summary of data stored for the given user.

        Args:
            telegram_user_id: Numeric Telegram user ID.

        Returns:
            Dict with keys ``total_figurinhas``, ``possuidas``,
            ``total_exemplares``, ``total_movimentacoes``,
            ``primeira_movimentacao``, ``ultima_movimentacao``.
        """
        sql_fig = (
            "SELECT COUNT(*), "
            "COUNT(*) FILTER (WHERE quantidade > 0), "
            "COALESCE(SUM(quantidade), 0) "
            "FROM figurinhas WHERE telegram_user_id = %s"
        )
        sql_mov = (
            "SELECT COUNT(*), MIN(created_at), MAX(created_at) "
            "FROM movimentacoes WHERE telegram_user_id = %s"
        )
        with self._conn.cursor() as cur:
            cur.execute(sql_fig, (telegram_user_id,))
            row_fig = cur.fetchone()
            cur.execute(sql_mov, (telegram_user_id,))
            row_mov = cur.fetchone()

        return {
            "telegram_user_id": telegram_user_id,
            "total_figurinhas": int(row_fig[0]) if row_fig else 0,
            "possuidas": int(row_fig[1]) if row_fig else 0,
            "total_exemplares": int(row_fig[2]) if row_fig else 0,
            "total_movimentacoes": int(row_mov[0]) if row_mov else 0,
            "primeira_movimentacao": row_mov[1] if row_mov else None,
            "ultima_movimentacao": row_mov[2] if row_mov else None,
        }

    def excluir_usuario(self, telegram_user_id: int) -> tuple[int, int]:
        """Delete all data for the given user (movimentacoes then figurinhas).

        Deletes in FK-safe order: movimentacoes first, then figurinhas.
        Does not commit — the caller is responsible for committing.

        Args:
            telegram_user_id: Numeric Telegram user ID.

        Returns:
            Tuple ``(movimentacoes_deleted, figurinhas_deleted)``.

        Raises:
            psycopg2.DatabaseError: On any database error; connection is
                rolled back before re-raising.
        """
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM movimentacoes WHERE telegram_user_id = %s",
                    (telegram_user_id,),
                )
                mov_del = cur.rowcount
                cur.execute(
                    "DELETE FROM figurinhas WHERE telegram_user_id = %s",
                    (telegram_user_id,),
                )
                fig_del = cur.rowcount
            logger.info("excluir_usuario: user=%d mov_del=%d fig_del=%d", telegram_user_id, mov_del, fig_del)
            return mov_del, fig_del
        except psycopg2.DatabaseError:
            self._conn.rollback()
            logger.exception("excluir_usuario: rollback — user=%d", telegram_user_id)
            raise

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

    @staticmethod
    def _build_album_rows(telegram_user_id: int, stickers: list[dict]) -> list[tuple]:
        """Build the list of row tuples for batch-inserting album stickers.

        Args:
            telegram_user_id: Numeric Telegram user ID owning the new rows.
            stickers: List of dicts with keys: ``grupo``, ``codigo_selecao``,
                ``nome_selecao``, ``numero``, ``codigo_figurinha``, ``pagina``.

        Returns:
            List of tuples matching the ``_SQL_INIT_ALBUM`` placeholder order.
        """
        return [
            (
                telegram_user_id,
                s["grupo"],
                s["codigo_selecao"],
                s["nome_selecao"],
                s["numero"],
                s["codigo_figurinha"],
                s["pagina"],
            )
            for s in stickers
        ]

    def inicializar_album(self, telegram_user_id: int, stickers: list[dict]) -> None:
        """Batch-insert all sticker rows for a new user with quantidade=0.

        Args:
            telegram_user_id: Numeric Telegram user ID owning the new rows.
            stickers: List of dicts with keys: ``grupo``, ``codigo_selecao``,
                ``nome_selecao``, ``numero``, ``codigo_figurinha``, ``pagina``.

        Raises:
            psycopg2.DatabaseError: If the database rejects the batch insert.
                The connection is rolled back before re-raising.
        """
        rows = self._build_album_rows(telegram_user_id, stickers)
        try:
            with self._conn.cursor() as cur:
                cur.executemany(_SQL_INIT_ALBUM, rows)
            logger.debug("inicializar_album: %d stickers for user=%d", len(rows), telegram_user_id)
        except psycopg2.DatabaseError:
            self._conn.rollback()
            logger.exception(
                "inicializar_album: rollback — user=%d stickers=%d",
                telegram_user_id,
                len(rows),
            )
            raise
