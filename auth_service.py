"""Astro-Zodiac T13 — authentication domain service.

The service is repository-driven so HTTP framework and database choices can be
plugged in later without changing authentication rules.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import UUID

from auth_security import hash_password, hash_token, new_opaque_token, normalize_email, verify_password
from user_schema import UserAccount, utc_now


class AuthRepository(Protocol):
    def get_user_by_email(self, email: str) -> UserAccount | None: ...
    def get_user(self, user_id: UUID) -> UserAccount | None: ...
    def create_user(self, user: UserAccount, password_hash: str) -> None: ...
    def get_password_hash(self, user_id: UUID) -> str | None: ...
    def save_session(self, token_hash: str, user_id: UUID, expires_at: datetime) -> None: ...
    def get_session_user(self, token_hash: str, now: datetime) -> UUID | None: ...


class AuthError(ValueError):
    pass


def register(repo: AuthRepository, email: str, password: str, display_name: str = "") -> UserAccount:
    normalized = normalize_email(email)
    if repo.get_user_by_email(normalized) is not None:
        raise AuthError("email already registered")
    user = UserAccount(email=normalized, display_name=display_name, status="active")
    repo.create_user(user, hash_password(password))
    return user


def authenticate(repo: AuthRepository, email: str, password: str) -> UserAccount:
    normalized = normalize_email(email)
    user = repo.get_user_by_email(normalized)
    if user is None:
        raise AuthError("invalid credentials")
    if user.status != "active":
        raise AuthError("account is not active")
    password_hash = repo.get_password_hash(user.user_id)
    if password_hash is None or not verify_password(password, password_hash):
        raise AuthError("invalid credentials")
    user.last_login_at = utc_now()
    return user


def create_session(repo: AuthRepository, user_id: UUID, ttl_hours: int = 24 * 7) -> str:
    if ttl_hours <= 0:
        raise ValueError("ttl_hours must be positive")
    token = new_opaque_token()
    repo.save_session(hash_token(token), user_id, utc_now() + timedelta(hours=ttl_hours))
    return token


def resolve_session(repo: AuthRepository, token: str) -> UserAccount | None:
    if not token:
        return None
    user_id = repo.get_session_user(hash_token(token), utc_now())
    return repo.get_user(user_id) if user_id else None


def revoke_password_reset_token(token: str) -> str:
    """Return only a hash suitable for persistence; never persist the raw token."""
    return hash_token(token)
