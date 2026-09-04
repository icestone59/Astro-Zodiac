"""Astro-Zodiac T13 — membership/ownership contracts.

T13 records who owns what. Payment state is supplied by the future billing layer.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

MembershipStatus = Literal["active", "past_due", "canceled", "expired", "revoked"]
GrantSource = Literal["system", "payment", "manual", "promo", "migration"]
BillingInterval = Literal["none", "month", "year", "lifetime"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MembershipPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(min_length=2, max_length=64)
    product_id: str = Field(min_length=2, max_length=64)
    billing_interval: BillingInterval = "none"
    active: bool = True


class MembershipGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    membership_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    product_id: str
    status: MembershipStatus = "active"
    source: GrantSource = "system"
    starts_at: datetime = Field(default_factory=utc_now)
    ends_at: datetime | None = None
    external_reference: str | None = None


class MembershipState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    active_products: list[str] = Field(default_factory=lambda: ["free"])
    grants: list[MembershipGrant] = Field(default_factory=list)

    def has_product(self, product_id: str, now: datetime | None = None) -> bool:
        now = now or utc_now()
        if product_id == "free":
            return True
        for grant in self.grants:
            if grant.product_id != product_id or grant.status != "active":
                continue
            if grant.starts_at > now:
                continue
            if grant.ends_at is not None and grant.ends_at <= now:
                continue
            return True
        return False


class MembershipDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    product_id: str
    reason: str
