"""Astro-Zodiac T13 — user/account contracts.

Framework-agnostic domain models. Persistence and HTTP routes stay outside T13.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["user", "professional", "admin"]
AccountStatus = Literal["active", "pending_verification", "locked", "disabled"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    display_name: str = Field(default="", max_length=120)
    role: UserRole = "user"
    status: AccountStatus = "active"
    email_verified: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    last_login_at: datetime | None = None


class UserProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    display_name: str = Field(default="", max_length=120)
    locale: str = Field(default="th-TH", max_length=16)
    timezone: str = Field(default="Asia/Bangkok", max_length=64)


class BirthDataRef(BaseModel):
    """Reference only; canonical birth-chart contract remains in T1/T2."""
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    chart_id: str | None = None
