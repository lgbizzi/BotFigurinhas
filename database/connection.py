"""PostgreSQL connection pool management.

Provides a thread-safe Singleton connection pool backed by
:class:`psycopg2.pool.ThreadedConnectionPool`.  All database credentials are
read exclusively from :mod:`config.settings`; no credentials are accepted as
arguments.

Typical usage::

    from database.connection import ConnectionPool

    pool = ConnectionPool.get_instance()
    conn = pool.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    finally:
        pool.release_connection(conn)
"""

import logging
import threading
from typing import Optional

import psycopg2
import psycopg2.pool
from psycopg2.extensions import connection as PsycopgConnection

import config.settings as settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ConnectionPoolError(Exception):
    """Raised when the connection pool cannot be initialised or accessed."""


class ConnectionAcquisitionError(ConnectionPoolError):
    """Raised when a connection cannot be acquired from the pool."""


# ---------------------------------------------------------------------------
# Singleton pool
# ---------------------------------------------------------------------------


class ConnectionPool:
    """Thread-safe Singleton wrapper around :class:`psycopg2.pool.ThreadedConnectionPool`.

    The pool is created lazily on the first call to :meth:`get_instance` and
    is shared across all threads in the same process.

    Example::

        pool = ConnectionPool.get_instance()
        conn = pool.get_connection()
        try:
            # … use conn …
        finally:
            pool.release_connection(conn)
    """

    _instance: Optional["ConnectionPool"] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        """Initialise the underlying ThreadedConnectionPool.

        Raises:
            ConnectionPoolError: If the pool cannot be created (e.g. wrong
                credentials or database unreachable).
        """
        logger.info(
            "Initialising PostgreSQL connection pool — host=%s port=%d db=%s "
            "pool_min=%d pool_max=%d",
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
            settings.DB_POOL_MIN,
            settings.DB_POOL_MAX,
        )
        try:
            self._pool: psycopg2.pool.ThreadedConnectionPool = (
                psycopg2.pool.ThreadedConnectionPool(
                    minconn=settings.DB_POOL_MIN,
                    maxconn=settings.DB_POOL_MAX,
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    dbname=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                )
            )
        except psycopg2.OperationalError as exc:
            raise ConnectionPoolError(
                f"Failed to create connection pool: {exc}. "
                "Check that the PostgreSQL server is reachable and that the "
                "credentials in your environment variables are correct."
            ) from exc

    @classmethod
    def get_instance(cls) -> "ConnectionPool":
        """Return the shared :class:`ConnectionPool` instance, creating it if needed.

        Thread-safe: uses a lock to prevent double-initialisation.

        Returns:
            The singleton :class:`ConnectionPool`.

        Raises:
            ConnectionPoolError: If the pool cannot be created.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_connection(self) -> PsycopgConnection:
        """Acquire a connection from the pool.

        Returns:
            An open :class:`psycopg2.extensions.connection`.

        Raises:
            ConnectionAcquisitionError: If no connection is available (pool
                exhausted or closed).
        """
        try:
            conn: PsycopgConnection = self._pool.getconn()
        except psycopg2.pool.PoolError as exc:
            raise ConnectionAcquisitionError(
                f"Could not acquire a database connection from the pool: {exc}. "
                "The pool may be exhausted; consider increasing DB_POOL_MAX."
            ) from exc

        logger.debug("Connection acquired from pool: %s", id(conn))
        return conn

    def release_connection(self, conn: PsycopgConnection) -> None:
        """Return a connection to the pool.

        Args:
            conn: The connection previously obtained via :meth:`get_connection`.
        """
        self._pool.putconn(conn)
        logger.debug("Connection returned to pool: %s", id(conn))

    def close_all(self) -> None:
        """Close all connections in the pool and destroy the singleton.

        After calling this method a new pool will be created on the next call
        to :meth:`get_instance`.
        """
        logger.info("Closing all connections in the pool.")
        self._pool.closeall()
        with self.__class__._lock:
            self.__class__._instance = None
