"""Astro-Zodiac T17 — small persistence adapters for core account/billing data.

The repository uses simple SQL and parameter binding; domain objects remain
owned by T12–T15. More domain-specific repositories can be added later without
moving SQL into the HTTP layer.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping


class PostgresRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def create_user(self, *, user_id: str, email: str, display_name: str,
                    role: str, status: str, email_verified: bool,
                    created_at: datetime) -> None:
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users
                    (user_id, email, display_name, role, status, email_verified, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, email, display_name, role, status, email_verified, created_at),
            )

    def get_user_by_email(self, email: str) -> Mapping[str, Any] | None:
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT user_id, email, display_name, role, status, email_verified, created_at, last_login_at "
                "FROM users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            columns = ["user_id", "email", "display_name", "role", "status", "email_verified", "created_at", "last_login_at"]
            return dict(zip(columns, row))

    def record_ai_usage(self, *, usage_event_id: str, user_id: str, product_id: str,
                        usage_type: str, quantity: int, success: bool,
                        request_id: str | None, created_at: datetime) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ai_usage_events
                    (usage_event_id, user_id, product_id, usage_type, quantity, success, request_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (usage_event_id, user_id, product_id, usage_type, quantity, success, request_id, created_at),
            )

    def save_order(self, *, order_id: str, user_id: str, product_id: str,
                   amount_minor: int, currency: str, status: str,
                   provider: str | None, provider_payment_id: str | None,
                   created_at: datetime, paid_at: datetime | None,
                   metadata: Mapping[str, Any]) -> None:
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders
                    (order_id, user_id, product_id, amount_minor, currency, status,
                     provider, provider_payment_id, created_at, paid_at, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    provider = EXCLUDED.provider,
                    provider_payment_id = EXCLUDED.provider_payment_id,
                    paid_at = EXCLUDED.paid_at,
                    metadata = EXCLUDED.metadata
                """,
                (order_id, user_id, product_id, amount_minor, currency, status,
                 provider, provider_payment_id, created_at, paid_at, dict(metadata)),
            )

    def record_webhook_event(self, *, event_id: str, provider: str,
                             event_type: str, status: str,
                             received_at: datetime,
                             provider_payment_id: str | None,
                             payload: Mapping[str, Any]) -> bool:
        """Return True when inserted, False when the event already exists."""
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO webhook_events
                    (event_id, provider, event_type, status, received_at,
                     provider_payment_id, payload)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (provider, event_id) DO NOTHING
                RETURNING event_id
                """,
                (event_id, provider, event_type, status, received_at,
                 provider_payment_id, dict(payload)),
            )
            return cur.fetchone() is not None
