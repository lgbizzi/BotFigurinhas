"""Seed script: populate the ``figurinhas`` table from :mod:`seeds.album_data`.

Idempotent — re-running this script never duplicates rows because the INSERT
uses ``ON CONFLICT (codigo_figurinha) DO NOTHING``.

Usage::

    python seeds/seed_figurinhas.py

The script must be executed from the project root so that the relative imports
resolve correctly, or :envvar:`PYTHONPATH` must include the project root.
"""

import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path when run as __main__
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Stdlib / project imports (after path fix)
# ---------------------------------------------------------------------------
import psycopg2

from database.connection import ConnectionPool, ConnectionPoolError
from seeds.album_data import ALBUM_GROUPS, TOTAL_FIGURINHAS

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQL constants
# ---------------------------------------------------------------------------
_TABLE_FIGURINHAS = "figurinhas"

_SQL_INSERT_FIGURINHA = f"""
INSERT INTO {_TABLE_FIGURINHAS}
    (grupo, codigo_selecao, nome_selecao, numero, codigo_figurinha, quantidade)
VALUES
    (%(grupo)s, %(codigo_selecao)s, %(nome_selecao)s, %(numero)s, %(codigo_figurinha)s, 0)
ON CONFLICT (codigo_figurinha) DO NOTHING;
"""


# ---------------------------------------------------------------------------
# Core seeding function
# ---------------------------------------------------------------------------


def seed_figurinhas() -> None:
    """Insert all album stickers into the ``figurinhas`` table.

    Iterates over every entry in :data:`seeds.album_data.ALBUM_GROUPS`,
    builds the ``codigo_figurinha`` key (``<codigo_selecao>-<numero>``), and
    performs a conflict-safe INSERT.  Progress is logged per group and a
    summary is printed at the end.

    Raises:
        ConnectionPoolError: If the database connection pool cannot be
            initialised.
        psycopg2.DatabaseError: If any SQL statement fails unexpectedly.
    """
    logger.info(
        "Starting seed — %d stickers to process across %d entries.",
        TOTAL_FIGURINHAS,
        len(ALBUM_GROUPS),
    )

    pool = ConnectionPool.get_instance()
    conn = pool.get_connection()

    total_inserted = 0

    try:
        with conn:  # auto-commits on success, rolls back on exception
            with conn.cursor() as cur:
                for group in ALBUM_GROUPS:
                    group_inserted = 0

                    for numero in group.numeros:
                        codigo_figurinha = f"{group.codigo_selecao}-{numero}"
                        cur.execute(
                            _SQL_INSERT_FIGURINHA,
                            {
                                "grupo": group.grupo,
                                "codigo_selecao": group.codigo_selecao,
                                "nome_selecao": group.nome_selecao,
                                "numero": numero,
                                "codigo_figurinha": codigo_figurinha,
                            },
                        )
                        group_inserted += cur.rowcount  # 1 if inserted, 0 if skipped

                    total_inserted += group_inserted
                    logger.info(
                        "Group %-3s | %-5s | %-25s | %2d/%2d rows inserted",
                        group.grupo,
                        group.codigo_selecao,
                        group.nome_selecao,
                        group_inserted,
                        len(group.numeros),
                    )

    except psycopg2.DatabaseError as exc:
        logger.exception("Database error during seed: %s", exc)
        raise
    finally:
        pool.release_connection(conn)

    logger.info(
        "Seed complete — %d/%d stickers inserted (skipped: %d).",
        total_inserted,
        TOTAL_FIGURINHAS,
        TOTAL_FIGURINHAS - total_inserted,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        seed_figurinhas()
    except (ConnectionPoolError, psycopg2.DatabaseError) as exc:
        logger.error("Seed failed: %s", exc)
        sys.exit(1)
