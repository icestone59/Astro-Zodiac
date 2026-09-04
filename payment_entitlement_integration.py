"""Astro-Zodiac T15 — payment to membership/entitlement integration.

This module is a deterministic domain adapter between T14 payment state and
T13 membership ownership. Payment confirmation is authoritative for granting
paid product ownership; entitlement checks remain delegated to T12/T13.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from membership_schema import MembershipGrant, MembershipState
from membership_service import grant_membership
from payment_schema import Order, OrderStatus, Payment, PaymentStatus
from product_catalog import get_product


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _is_paid_product(product_id: str) -> bool:
    return product_id != "free"


def _grant_reference(order: Order) -> str:
    return f"order:{order.order_id}"


def _find_grant_by_reference(state: MembershipState, reference: str) -> Optional[MembershipGrant]:
    for grant in state.grants:
        if grant.external_reference == reference:
            return grant
    return None


def _rebuild_active_products(state: MembershipState, now: Optional[datetime] = None) -> None:
    now = now or utc_now()
    products = {"free"}
    for grant in state.grants:
        if grant.status != "active":
            continue
        if grant.starts_at > now:
            continue
        if grant.ends_at is not None and grant.ends_at <= now:
            continue
        products.add(grant.product_id)
    state.active_products = sorted(products)


@dataclass(frozen=True)
class IntegrationResult:
    action: str
    product_id: str
    grant: MembershipGrant | None
    reason: str


def grant_after_successful_payment(
    state: MembershipState,
    order: Order,
    payment: Payment,
) -> IntegrationResult:
    """Grant the purchased product after a verified successful payment.

    Idempotent by order_id/external_reference. Reprocessing the same paid order
    returns the existing grant instead of creating a duplicate membership.
    """
    if order.user_id != str(state.user_id) and order.user_id != state.user_id.__str__():
        raise ValueError("order user does not match membership state user")
    if order.status != OrderStatus.PAID:
        raise ValueError("order is not paid")
    if payment.status != PaymentStatus.SUCCEEDED:
        raise ValueError("payment is not succeeded")
    if payment.order_id != order.order_id or payment.user_id != order.user_id:
        raise ValueError("payment does not match order")

    product = get_product(order.product_id)
    if not _is_paid_product(product.product_id):
        raise ValueError("free product should not be granted from payment")

    reference = _grant_reference(order)
    existing = _find_grant_by_reference(state, reference)
    if existing is not None:
        _rebuild_active_products(state)
        return IntegrationResult(
            action="already_granted",
            product_id=product.product_id,
            grant=existing,
            reason="payment was already converted to a membership grant",
        )

    grant = grant_membership(
        state,
        product_id=product.product_id,
        source="payment",
        starts_at=order.paid_at or utc_now(),
        external_reference=reference,
    )
    return IntegrationResult(
        action="granted",
        product_id=product.product_id,
        grant=grant,
        reason="successful payment granted product ownership",
    )


def revoke_after_refund(
    state: MembershipState,
    order: Order,
    payment: Payment,
) -> IntegrationResult:
    """Revoke only the grant created by the refunded order.

    This intentionally does not call the broad T13 revoke_membership helper,
    because a user may have multiple valid purchases of the same product.
    """
    if payment.order_id != order.order_id or payment.user_id != order.user_id:
        raise ValueError("payment does not match order")
    if payment.status != PaymentStatus.REFUNDED and order.status != OrderStatus.REFUNDED:
        raise ValueError("payment/order is not refunded")

    reference = _grant_reference(order)
    grant = _find_grant_by_reference(state, reference)
    if grant is None:
        _rebuild_active_products(state)
        return IntegrationResult(
            action="no_grant",
            product_id=order.product_id,
            grant=None,
            reason="no payment-created grant exists for this order",
        )

    if grant.status != "active":
        _rebuild_active_products(state)
        return IntegrationResult(
            action="already_revoked",
            product_id=order.product_id,
            grant=grant,
            reason="grant is no longer active",
        )

    grant.status = "revoked"
    _rebuild_active_products(state)
    return IntegrationResult(
        action="revoked",
        product_id=order.product_id,
        grant=grant,
        reason="refunded payment revoked the linked membership grant",
    )
