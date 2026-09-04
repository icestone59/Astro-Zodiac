"""T21.1 runtime policy: PostgreSQL is the only runtime persistence backend."""
from __future__ import annotations

import os


def runtime_environment() -> str:
    return os.getenv("ASTRO_ZODIAC_ENV", "development").strip().lower()


def persistence_mode() -> str:
    # Kept as an env variable for observability/backwards compatibility, but the
    # runtime policy no longer permits memory persistence outside tests.
    return os.getenv("ASTRO_ZODIAC_PERSISTENCE", "postgres").strip().lower()


def validate_runtime_config() -> None:
    mode = persistence_mode()
    if mode != "postgres":
        raise RuntimeError(
            "PostgreSQL is the only runtime persistence backend. "
            "Set ASTRO_ZODIAC_PERSISTENCE=postgres."
        )
    if not os.getenv("DATABASE_URL", "").strip():
        raise RuntimeError("PostgreSQL runtime requires DATABASE_URL")
