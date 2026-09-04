"""Astro-Zodiac T13 — membership ownership service."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from membership_schema import MembershipDecision, MembershipGrant, MembershipState


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def grant_membership(
    state: MembershipState,
    product_id: str,
    source: str = "manual",
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    external_reference: str | None = None,
) -> MembershipGrant:
    grant = MembershipGrant(
        user_id=state.user_id,
        product_id=product_id,
        source=source,
        starts_at=starts_at or utc_now(),
        ends_at=ends_at,
        external_reference=external_reference,
    )
    state.grants.append(grant)
    if product_id not in state.active_products:
        state.active_products.append(product_id)
    return grant


def revoke_membership(state: MembershipState, product_id: str) -> int:
    changed = 0
    for grant in state.grants:
        if grant.product_id == product_id and grant.status == "active":
            grant.status = "revoked"
            changed += 1
    state.active_products = [p for p in state.active_products if p != product_id or p == "free"]
    return changed


def check_membership(state: MembershipState, product_id: str) -> MembershipDecision:
    allowed = state.has_product(product_id)
    return MembershipDecision(
        allowed=allowed,
        product_id=product_id,
        reason="active membership" if allowed else "product not owned or expired",
    )
