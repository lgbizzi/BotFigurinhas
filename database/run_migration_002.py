"""Run database migration 002: per-user album isolation.

Reads credentials from a ``.env`` file in the project root, connects to
PostgreSQL via psycopg2, executes ``database/migrations/002_per_user_album.sql``,
and commits the transaction.

Usage::

    python database/run_migration_002.py

The script must be executed from the project root, or :envvar:`PYTHONPATH`
must include the project root so that the relative path resolution works.
"""

import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
import os

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_MIGRATION_FILE = _PROJECT_ROOT / "database" / "migrations" / "002_per_user_album.sql"
_ENV_FILE = _PROJECT_ROOT / ".env"


def main() -> None:
    """Load credentials, execute the migration SQL, and commit.

    Raises:
        SystemExit: On any connection or execution error.
    """
    load_dotenv(dotenv_path=_ENV_FILE)

    host = os.environ["POSTGRES_HOST"]
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    sql = _MIGRATION_FILE.read_text(encoding="utf-8")

    try:
        with psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
    except psycopg2.Error as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Migration 002 applied successfully.")


if __name__ == "__main__":
    main()
