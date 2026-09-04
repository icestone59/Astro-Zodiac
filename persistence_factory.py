"""T21.1 runtime persistence: PostgreSQL only.

In-memory repositories are intentionally not exposed through the runtime factory.
Tests may instantiate test doubles directly, but the application runtime must use
PostgreSQL in development, staging, and production.
"""
from __future__ import annotations

from contextlib import contextmanager
from postgres_auth_repository import PostgresAuthRepository
from postgres_membership_repository import PostgresMembershipRepository
from postgres_connection import connection


@contextmanager
def auth_repository():
    with connection() as conn:
        yield PostgresAuthRepository(conn)


@contextmanager
def membership_repository():
    with connection() as conn:
        yield PostgresMembershipRepository(conn)
