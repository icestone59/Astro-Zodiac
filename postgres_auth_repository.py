"""PostgreSQL adapter for the T13 authentication contract.

Runtime-only adapter. The application layer owns the repository lifetime.
This adapter matches the actual T17/T19 schema:
  users.user_id
  users.password_hash
  user_sessions.token_hash
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from auth_security import hash_password, verify_password
from user_schema import UserAccount


class PostgresAuthRepository:
    def __init__(self, conn):
        self.conn = conn

    def ping(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

    def get_user(self, user_id: UUID) -> UserAccount | None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, email, display_name, role, status,
                       email_verified, created_at, last_login_at
                FROM users
                WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return UserAccount(
            user_id=row[0],
            email=row[1],
            display_name=row[2] or "",
            role=row[3],
            status=row[4],
            email_verified=bool(row[5]),
            created_at=row[6],
            last_login_at=row[7],
        )

    def get_user_by_email(self, email: str) -> UserAccount | None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, email, display_name, role, status,
                       email_verified, created_at, last_login_at
                FROM users
                WHERE lower(email) = lower(%s)
                """,
                (email,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return UserAccount(
            user_id=row[0],
            email=row[1],
            display_name=row[2] or "",
            role=row[3],
            status=row[4],
            email_verified=bool(row[5]),
            created_at=row[6],
            last_login_at=row[7],
        )

    def get_password_hash(self, user_id: UUID) -> str | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
        return row[0] if row and row[0] else None

    def create_user(self, user: UserAccount, password_hash: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users
                    (user_id, email, display_name, role, status,
                     email_verified, created_at, last_login_at,
                     password_hash)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user.user_id,
                    str(user.email),
                    user.display_name,
                    user.role,
                    user.status,
                    user.email_verified,
                    user.created_at,
                    user.last_login_at,
                    password_hash,
                ),
            )

    def save_session(
        self,
        token_hash: str,
        user_id: UUID,
        expires_at: datetime,
    ) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_sessions
                    (token_hash, user_id, expires_at, created_at, revoked_at)
                VALUES
                    (%s, %s, %s, NOW(), NULL)
                """,
                (token_hash, user_id, expires_at),
            )

    def get_session_user(
        self,
        token_hash: str,
        now: datetime,
    ) -> UUID | None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id
                FROM user_sessions
                WHERE token_hash = %s
                  AND expires_at > %s
                  AND revoked_at IS NULL
                """,
                (token_hash, now),
            )
            row = cur.fetchone()

        return row[0] if row else None

    # Compatibility helpers used by earlier runtime experiments. Keep them
    # thin so they cannot diverge from the canonical T13 contract.
    def verify_user(self, email: str, password: str) -> UserAccount | None:
        user = self.get_user_by_email(email)
        if not user:
            return None
        password_hash = self.get_password_hash(user.user_id)
        if not password_hash or not verify_password(password, password_hash):
            return None
        return user
