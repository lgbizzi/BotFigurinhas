"""Abstract base class for all repositories in the Album Copa 2026 project.

Defines the minimum common contract that every repository must satisfy.
Concrete implementations receive an open database connection via their
constructor (Dependency Inversion Principle) and are responsible solely for
persistence and retrieval — no business logic.
"""

import abc

import psycopg2.extensions


class BaseRepository(abc.ABC):
    """Abstract base for psycopg2-backed repositories.

    Every repository:
    - Receives an open :class:`psycopg2.extensions.connection` at construction
      time (DIP — connection is injected, never created internally).
    - Contains all SQL for its entity — no SQL leaks into services or DAGs.
    - Implements explicit transaction management (commit / rollback) for every
      write operation.

    Subclasses must call ``super().__init__(connection)`` to store ``self._conn``.
    """

    def __init__(self, connection: psycopg2.extensions.connection) -> None:
        """Store the injected database connection.

        Args:
            connection: An open psycopg2 connection.  The repository does
                **not** own the connection lifecycle — the caller is responsible
                for closing it.
        """
        self._conn = connection

    def commit(self) -> None:
        """Commit the current database transaction.

        Called by the service layer after all writes in a unit of work
        complete successfully.
        """
        self._conn.commit()

    def rollback(self) -> None:
        """Roll back the current database transaction.

        Called by the service layer when any write in a unit of work fails,
        restoring the database to its state before the operation began.
        """
        self._conn.rollback()
