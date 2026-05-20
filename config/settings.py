"""Application settings loaded from environment variables.

Reads configuration using python-dotenv. All mandatory variables must be
present in the environment (or in a .env file) before this module is imported;
a missing variable raises :class:`EnvironmentError` immediately so the
application fails fast instead of surfacing cryptic errors at runtime.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require(name: str) -> str:
    """Return the value of an environment variable or raise EnvironmentError.

    Args:
        name: Name of the environment variable.

    Returns:
        The string value of the variable.

    Raises:
        EnvironmentError: If the variable is absent or empty.
    """
    value = os.getenv(name, "").strip()
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            "Ensure it is defined in your .env file or exported in the shell."
        )
    return value


def _optional_int(name: str, default: int) -> int:
    """Return the integer value of an optional environment variable.

    Args:
        name: Name of the environment variable.
        default: Value to use when the variable is absent.

    Returns:
        Parsed integer value.

    Raises:
        ValueError: If the variable is present but cannot be parsed as int.
    """
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{name}' must be an integer, got: {raw!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Mandatory settings
# ---------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")

DB_HOST: str = _require("POSTGRES_HOST")
DB_PORT: int = _optional_int("POSTGRES_PORT", 5432)
DB_NAME: str = _require("POSTGRES_DB")
DB_USER: str = _require("POSTGRES_USER")
DB_PASSWORD: str = _require("POSTGRES_PASSWORD")

# ---------------------------------------------------------------------------
# Optional settings with defaults
# ---------------------------------------------------------------------------

DB_POOL_MIN: int = _optional_int("DB_POOL_MIN", 1)
DB_POOL_MAX: int = _optional_int("DB_POOL_MAX", 10)
