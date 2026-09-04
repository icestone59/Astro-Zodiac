"""Astro-Zodiac T17 — PostgreSQL connection boundary.

The module keeps the driver dependency optional until deployment. Production
should install psycopg 3 and provide DATABASE_URL through the environment.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator


class DatabaseConfigurationError(RuntimeError):
    pass


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise DatabaseConfigurationError("DATABASE_URL is not configured")
    return url


def connect() -> Any:
    try:
        import psycopg  # type: ignore
    except ImportError as exc:
        raise DatabaseConfigurationError(
            "psycopg is required for PostgreSQL runtime; install requirements-t17.txt"
        ) from exc
    return psycopg.connect(get_database_url())


@contextmanager
def connection() -> Iterator[Any]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
