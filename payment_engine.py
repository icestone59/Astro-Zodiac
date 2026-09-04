"""Astro-Zodiac T14 — provider-neutral payment/order domain engine."""
from __future__ import annotations
import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Dict, Optional, Protocol, Tuple

from payment_schema import (
    Money, Order, OrderStatus, Payment, PaymentStatus,
    WebhookEvent, WebhookProcessingStatus, WebhookRecord,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


class PaymentProviderAdapter(Protocol):
    name: str
    def create_payment(self, order: Order) -> Tuple[str, PaymentStatus]: ...
    def verify_webhook(self, raw_body: bytes, signature: str) -> bool: ...
    def parse_webhook(self, raw_body: bytes) -> WebhookEvent: ...


class InMemoryPaymentStore:
    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}
        self.payments: Dict[str, Payment] = {}
        self.events: Dict[str, WebhookRecord] = {}


class PaymentEngine:
    """Domain operations only. HTTP, provider SDKs and entitlement grants stay outside."""

    def __init__(self, store: Optional[InMemoryPaymentStore] = None) -> None:
        self.store = store or InMemoryPaymentStore()

    def create_order(self, user_id: str, product_id: str, amount: Money) -> Order:
        if not user_id or not product_id:
            raise ValueError("user_id and product_id are required")
        order = Order(generate_id("ord"), user_id, product_id, amount)
        self.store.orders[order.order_id] = order
        return order

    def attach_payment(self, order_id: str, provider: str, provider_payment_id: str,
                       status: PaymentStatus) -> Payment:
        order = self._get_order(order_id)
        if order.status in {OrderStatus.CANCELLED, OrderStatus.REFUNDED, OrderStatus.EXPIRED}:
            raise ValueError("cannot attach payment to terminal order")
        payment = Payment(
            payment_id=generate_id("pay"),
            order_id=order.order_id,
            user_id=order.user_id,
            provider=provider,
            provider_payment_id=provider_payment_id,
            amount=order.amount,
            status=status,
        )
        self.store.payments[payment.payment_id] = payment
        order.provider = provider
        order.provider_payment_id = provider_payment_id
        order.status = self._order_status_for_payment(status)
        if status == PaymentStatus.SUCCEEDED:
            order.paid_at = _utc_now()
        return payment

    def process_webhook(self, event: WebhookEvent) -> WebhookRecord:
        # Idempotency: duplicate provider event must not grant twice downstream.
        existing = self.store.events.get(event.event_id)
        if existing:
            return existing

        record = WebhookRecord(event.event_id, event.provider, WebhookProcessingStatus.RECEIVED)
        self.store.events[event.event_id] = record
        try:
            payment = self._find_payment_by_provider_id(event.provider, event.provider_payment_id)
            if payment is None:
                record.status = WebhookProcessingStatus.IGNORED
                record.processed_at = _utc_now()
                record.error_code = "payment_not_found"
                return record

            next_status = self._map_event_to_payment_status(event.event_type)
            if next_status is None:
                record.status = WebhookProcessingStatus.IGNORED
                record.processed_at = _utc_now()
                record.error_code = "unsupported_event_type"
                return record

            self._apply_payment_status(payment, next_status)
            record.status = WebhookProcessingStatus.PROCESSED
            record.processed_at = _utc_now()
            return record
        except Exception:
            record.status = WebhookProcessingStatus.FAILED
            record.processed_at = _utc_now()
            record.error_code = "webhook_processing_error"
            raise

    def _apply_payment_status(self, payment: Payment, status: PaymentStatus) -> None:
        payment.status = status
        payment.updated_at = _utc_now()
        order = self._get_order(payment.order_id)
        order.status = self._order_status_for_payment(status)
        if status == PaymentStatus.SUCCEEDED and order.paid_at is None:
            order.paid_at = _utc_now()

    def _get_order(self, order_id: str) -> Order:
        try:
            return self.store.orders[order_id]
        except KeyError as exc:
            raise ValueError("order not found") from exc

    def _find_payment_by_provider_id(self, provider: str, provider_payment_id: Optional[str]) -> Optional[Payment]:
        if not provider_payment_id:
            return None
        for payment in self.store.payments.values():
            if payment.provider == provider and payment.provider_payment_id == provider_payment_id:
                return payment
        return None

    @staticmethod
    def _order_status_for_payment(status: PaymentStatus) -> OrderStatus:
        return {
            PaymentStatus.REQUIRES_ACTION: OrderStatus.PAYMENT_PENDING,
            PaymentStatus.PENDING: OrderStatus.PAYMENT_PENDING,
            PaymentStatus.SUCCEEDED: OrderStatus.PAID,
            PaymentStatus.FAILED: OrderStatus.FAILED,
            PaymentStatus.CANCELLED: OrderStatus.CANCELLED,
            PaymentStatus.REFUNDED: OrderStatus.REFUNDED,
        }[status]

    @staticmethod
    def _map_event_to_payment_status(event_type: str) -> Optional[PaymentStatus]:
        mapping = {
            "payment.succeeded": PaymentStatus.SUCCEEDED,
            "payment.failed": PaymentStatus.FAILED,
            "payment.cancelled": PaymentStatus.CANCELLED,
            "payment.refunded": PaymentStatus.REFUNDED,
            "payment.pending": PaymentStatus.PENDING,
            "payment.requires_action": PaymentStatus.REQUIRES_ACTION,
        }
        return mapping.get(event_type)


def verify_hmac_sha256(raw_body: bytes, signature: str, secret: str) -> bool:
    """Generic helper for providers that use HMAC-SHA256 signatures.
    Provider-specific canonicalization belongs in the adapter.
    """
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
