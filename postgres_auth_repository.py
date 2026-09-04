"""T19 PostgreSQL adapter implementing the T13 AuthRepository contract."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from user_schema import UserAccount


class PostgresAuthRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_user_by_email(self, email: str) -> UserAccount | None:
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT user_id, email, display_name, role, status, email_verified, created_at, last_login_at FROM users WHERE email = %s",
                (email.strip().lower(),),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return UserAccount(
            user_id=UUID(str(row[0])), email=row[1], display_name=row[2], role=row[3],
            status=row[4], email_verified=row[5], created_at=row[6], last_login_at=row[7]
        )

    def get_user(self, user_id: UUID) -> UserAccount | None:
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT user_id, email, display_name, role, status, email_verified, created_at, last_login_at FROM users WHERE user_id = %s",
                (str(user_id),),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return UserAccount(
            user_id=UUID(str(row[0])), email=row[1], display_name=row[2], role=row[3],
            status=row[4], email_verified=row[5], created_at=row[6], last_login_at=row[7]
        )

    def create_user(self, user: UserAccount, password_hash: str) -> None:
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO users (user_id,email,display_name,role,status,email_verified,created_at,password_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (str(user.user_id), str(user.email), user.display_name, user.role, user.status,
                 user.email_verified, user.created_at, password_hash),
            )

    def get_password_hash(self, user_id: UUID) -> str | None:
        with self.connection.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE user_id = %s", (str(user_id),))
            row = cur.fetchone()
        return row[0] if row else None

    def save_session(self, token_hash: str, user_id: UUID, expires_at: datetime) -> None:
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO user_sessions (token_hash,user_id,expires_at,created_at) VALUES (%s,%s,%s,%s)",
                (token_hash, str(user_id), expires_at, datetime.now(timezone.utc)),
            )

    def get_session_user(self, token_hash: str, now: datetime) -> UUID | None:
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM user_sessions WHERE token_hash = %s AND expires_at > %s AND revoked_at IS NULL",
                (token_hash, now),
            )
            row = cur.fetchone()
        return UUID(str(row[0])) if row else None
