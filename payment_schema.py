"""Astro-Zodiac T14 — Payment / Order contract.
Provider-neutral domain models; no gateway SDK or HTTP framework dependency.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentStatus(str, Enum):
    REQUIRES_ACTION = "requires_action"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class WebhookProcessingStatus(str, Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    IGNORED = "ignored"
    FAILED = "failed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Money:
    currency: str
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("amount must be non-negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("currency must be a 3-letter code")


@dataclass
class Order:
    order_id: str
    user_id: str
    product_id: str
    amount: Money
    status: OrderStatus = OrderStatus.PENDING
    provider: Optional[str] = None
    provider_payment_id: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)
    paid_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Payment:
    payment_id: str
    order_id: str
    user_id: str
    provider: str
    provider_payment_id: str
    amount: Money
    status: PaymentStatus
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WebhookEvent:
    event_id: str
    provider: str
    event_type: str
    provider_payment_id: Optional[str]
    payload: Dict[str, Any]
    received_at: datetime = field(default_factory=utc_now)


@dataclass
class WebhookRecord:
    event_id: str
    provider: str
    status: WebhookProcessingStatus
    processed_at: Optional[datetime] = None
    error_code: Optional[str] = None
