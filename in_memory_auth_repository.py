"""Small test/dev repository; replace with PostgreSQL adapter later."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from user_schema import UserAccount


class InMemoryAuthRepository:
    def __init__(self) -> None:
        self.users: dict[UUID, UserAccount] = {}
        self.password_hashes: dict[UUID, str] = {}
        self.email_index: dict[str, UUID] = {}
        self.sessions: dict[str, tuple[UUID, datetime]] = {}

    def get_user_by_email(self, email: str) -> UserAccount | None:
        user_id = self.email_index.get(email.strip().lower())
        return self.users.get(user_id) if user_id else None

    def get_user(self, user_id: UUID) -> UserAccount | None:
        return self.users.get(user_id)

    def create_user(self, user: UserAccount, password_hash: str) -> None:
        key = str(user.email).lower()
        if key in self.email_index:
            raise ValueError("duplicate email")
        self.users[user.user_id] = user
        self.password_hashes[user.user_id] = password_hash
        self.email_index[key] = user.user_id

    def get_password_hash(self, user_id: UUID) -> str | None:
        return self.password_hashes.get(user_id)

    def save_session(self, token_hash: str, user_id: UUID, expires_at: datetime) -> None:
        self.sessions[token_hash] = (user_id, expires_at)

    def get_session_user(self, token_hash: str, now: datetime) -> UUID | None:
        row = self.sessions.get(token_hash)
        if row is None:
            return None
        user_id, expires_at = row
        if expires_at <= now:
            self.sessions.pop(token_hash, None)
            return None
        return user_id
