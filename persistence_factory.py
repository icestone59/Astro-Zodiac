"""T19 runtime selection: PostgreSQL in production, in-memory only for explicit dev mode."""
from __future__ import annotations

import os
from contextlib import contextmanager

from in_memory_auth_repository import InMemoryAuthRepository
from postgres_auth_repository import PostgresAuthRepository
from postgres_membership_repository import PostgresMembershipRepository
from postgres_connection import connection


def persistence_mode() -> str:
    return os.getenv("ASTRO_ZODIAC_PERSISTENCE", "memory").strip().lower()


@contextmanager
def auth_repository():
    mode = persistence_mode()
    if mode == "postgres":
        with connection() as conn:
            yield PostgresAuthRepository(conn)
    else:
        if not hasattr(auth_repository, "_memory"):
            auth_repository._memory = InMemoryAuthRepository()
        yield auth_repository._memory


@contextmanager
def membership_repository():
    mode = persistence_mode()
    if mode != "postgres":
        yield None
        return
    with connection() as conn:
        yield PostgresMembershipRepository(conn)
