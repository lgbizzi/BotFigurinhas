"""Shared pytest fixtures for the Album Copa 2026 test suite.

Provides session-scoped database connectivity against an isolated PostgreSQL
test database and per-function fixtures for repository instances, mocks, and
sample domain objects.

Environment variables consumed (all required for integration tests):
    POSTGRES_TEST_HOST: Hostname of the PostgreSQL server (default: ``localhost``).
    POSTGRES_TEST_PORT: Port of the PostgreSQL server (default: ``5432``).
    POSTGRES_TEST_DB: Name of the **test** database (e.g. ``album_copa_test``).
    POSTGRES_TEST_USER: Database user with CREATE/DROP privileges.
    POSTGRES_TEST_PASSWORD: Password for the test user.

Isolation strategy:
    - A single connection is opened for the entire test session (``scope="session"``).
    - The schema is created once at session start from the canonical SQL migration.
    - Each integration test runs inside a savepoint (``SAVEPOINT`` / ``ROLLBACK TO
      SAVEPOINT``) so that every test sees a clean state without recreating tables.
    - A minimal seed row (BRA-1) is inserted after the schema is created and is
      restored for every test that needs a known-present figurinha.
"""

import os
import pathlib
from typing import Generator
from unittest.mock import MagicMock

import psycopg2
import psycopg2.extensions
import pytest

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / "database" / "migrations"

_MIGRATION_001_PATH = _MIGRATIONS_DIR / "001_initial_schema.sql"
_MIGRATION_002_PATH = _MIGRATIONS_DIR / "002_per_user_album.sql"
_MIGRATION_003_PATH = _MIGRATIONS_DIR / "003_add_pagina_to_figurinhas.sql"

_SEED_FIGURINHA_SQL = """
INSERT INTO figurinhas
    (telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, codigo_figurinha, quantidade, pagina)
VALUES (0, 'C', 'BRA', 'Brasil', 1, 'BRA-1', 0, 24)
ON CONFLICT (telegram_user_id, codigo_figurinha) DO NOTHING;
"""


def _get_test_dsn() -> dict[str, object]:
    """Build a psycopg2 connection keyword-argument dict from env vars.

    Returns:
        Dict suitable for passing to :func:`psycopg2.connect` as ``**kwargs``.
    """
    return {
        "host": os.getenv("POSTGRES_TEST_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_TEST_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_TEST_DB", "album_copa_test"),
        "user": os.getenv("POSTGRES_TEST_USER", "postgres"),
        "password": os.getenv("POSTGRES_TEST_PASSWORD", ""),
    }


def _aplicar_migracoes(conn: psycopg2.extensions.connection) -> None:
    """Apply all schema migrations and seed the minimum test row.

    Migrations 002 and 003 are applied only when their files exist so that the
    test suite can run in intermediate development states.

    Args:
        conn: Open psycopg2 connection; committed on success.
    """
    with conn.cursor() as cur:
        cur.execute(_MIGRATION_001_PATH.read_text(encoding="utf-8"))
        if _MIGRATION_002_PATH.exists():
            cur.execute(_MIGRATION_002_PATH.read_text(encoding="utf-8"))
        if _MIGRATION_003_PATH.exists():
            cur.execute(_MIGRATION_003_PATH.read_text(encoding="utf-8"))
        cur.execute(_SEED_FIGURINHA_SQL)
    conn.commit()


def _limpar_schema(conn: psycopg2.extensions.connection) -> None:
    """Drop all test tables and close the connection.

    Args:
        conn: Open psycopg2 connection; closed after teardown.
    """
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS movimentacoes CASCADE;")
        cur.execute("DROP TABLE IF EXISTS figurinhas CASCADE;")
        cur.execute("DROP FUNCTION IF EXISTS fn_figurinhas_set_updated_at() CASCADE;")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Session-scoped: real PostgreSQL connection
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Open a PostgreSQL connection to the isolated test database.

    Lifecycle (once per pytest session):
    1. Connect to the test database specified by ``POSTGRES_TEST_*`` env vars.
    2. Apply migrations in order: 001 (schema), 002 (per-user album), 003 (pagina).
       Migrations 002 and 003 are applied conditionally if the files exist.
    3. Insert the minimum seed row (BRA-1, telegram_user_id=0) required by tests.
    4. Yield the open connection to all tests.
    5. On teardown drop all test tables and close the connection.

    Yields:
        An open :class:`psycopg2.extensions.connection` in autocommit-OFF mode.

    Raises:
        psycopg2.OperationalError: If the test database is unreachable.
        EnvironmentError: If required env vars are missing.
    """
    dsn = _get_test_dsn()
    conn = psycopg2.connect(**dsn)
    conn.autocommit = False
    _aplicar_migracoes(conn)

    yield conn

    _limpar_schema(conn)


# ---------------------------------------------------------------------------
# Function-scoped: savepoint-based isolation for each integration test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=False)
def db_transaction(db_connection: psycopg2.extensions.connection) -> Generator[None, None, None]:
    """Wrap each test in a savepoint and roll back afterwards.

    This fixture must be requested explicitly by integration test modules (or
    via ``pytestmark``).  It ensures that every test starts with the same
    baseline state established by :func:`db_connection` without recreating the
    schema or reconnecting.

    Args:
        db_connection: Session-scoped open connection.

    Yields:
        Nothing — the fixture provides isolation as a side-effect.
    """
    with db_connection.cursor() as cur:
        cur.execute("SAVEPOINT test_savepoint;")
    yield
    with db_connection.cursor() as cur:
        cur.execute("ROLLBACK TO SAVEPOINT test_savepoint;")
        cur.execute("RELEASE SAVEPOINT test_savepoint;")


# ---------------------------------------------------------------------------
# Repository fixtures (real implementations, pointing to test DB)
# ---------------------------------------------------------------------------


@pytest.fixture
def figurinha_repository(db_connection: psycopg2.extensions.connection):
    """Return a :class:`FigurinhaRepository` wired to the test database.

    The repository module is imported inside the fixture so that this file can
    be collected even before the Backend Dev implements the module (RED phase).

    Args:
        db_connection: Session-scoped test database connection.

    Returns:
        A :class:`FigurinhaRepository` instance.
    """
    from repositories.figurinha_repository import FigurinhaRepository  # noqa: PLC0415

    return FigurinhaRepository(connection=db_connection)


@pytest.fixture
def movimentacao_repository(db_connection: psycopg2.extensions.connection):
    """Return a :class:`MovimentacaoRepository` wired to the test database.

    The repository module is imported inside the fixture so that this file can
    be collected even before the Backend Dev implements the module (RED phase).

    Args:
        db_connection: Session-scoped test database connection.

    Returns:
        A :class:`MovimentacaoRepository` instance.
    """
    from repositories.movimentacao_repository import MovimentacaoRepository  # noqa: PLC0415

    return MovimentacaoRepository(connection=db_connection)


# ---------------------------------------------------------------------------
# Mock fixtures for unit tests of services
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_figurinha_repository() -> MagicMock:
    """Return a :class:`unittest.mock.MagicMock` standing in for FigurinhaRepository.

    Intended for service-layer unit tests that must not touch a real database.

    Returns:
        A :class:`MagicMock` with no spec so all attribute accesses succeed.
    """
    return MagicMock(name="FigurinhaRepository")


@pytest.fixture
def mock_movimentacao_repository() -> MagicMock:
    """Return a :class:`unittest.mock.MagicMock` standing in for MovimentacaoRepository.

    Intended for service-layer unit tests that must not touch a real database.

    Returns:
        A :class:`MagicMock` with no spec so all attribute accesses succeed.
    """
    return MagicMock(name="MovimentacaoRepository")


# ---------------------------------------------------------------------------
# Domain object fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_figurinha():
    """Return a :class:`Figurinha` with valid, representative field values.

    The data matches the seed row inserted during session setup so integration
    tests can rely on this object being present in the test database.

    Returns:
        A :class:`Figurinha` instance for BRA-1 with ``quantidade=0``.
    """
    from datetime import datetime, timezone  # noqa: PLC0415

    from models.figurinha import Figurinha  # noqa: PLC0415

    now = datetime.now(tz=timezone.utc)
    return Figurinha(
        id=1,
        grupo="C",
        codigo_selecao="BRA",
        nome_selecao="Brasil",
        numero=1,
        codigo_figurinha="BRA-1",
        quantidade=0,
        pagina=24,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def user_info() -> dict[str, object]:
    """Return a minimal Telegram user info dict for use in movement tests.

    Returns:
        Dict with ``telegram_user_id`` and ``telegram_username`` keys.
    """
    return {
        "telegram_user_id": 123456789,
        "telegram_username": "test_user",
    }
