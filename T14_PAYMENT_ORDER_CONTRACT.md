# Astro-Zodiac T14 — Payment / Order / Webhook Contract

Status: Milestone / Baseline

## Purpose

Create a provider-neutral payment domain layer that can support one-time purchases and future recurring billing without coupling the core domain to a specific gateway.

## Scope

- Order lifecycle
- Payment lifecycle
- Provider payment reference
- Webhook event contract
- Webhook idempotency
- Generic signature helper
- Clear handoff point for entitlement granting

## Explicit non-scope

- No real payment gateway SDK
- No real HTTP routes
- No payment credentials
- No auto-grant from browser redirect
- No subscription implementation yet
- No PostgreSQL migration yet

## Security rules

1. Browser success/redirect is not proof of payment.
2. Backend webhook/provider verification is the source of truth for paid status.
3. Webhook processing must be idempotent by provider event ID.
4. Never store raw card details.
5. Provider-specific signature canonicalization belongs in an adapter.
6. Entitlement granting must happen only after a verified successful payment state.

## Lifecycle

```text
User
 ↓
Create Order
 ↓
Create Payment with Provider
 ↓
Provider Checkout
 ↓
Verified Webhook
 ↓
Payment = SUCCEEDED
 ↓
Order = PAID
 ↓
T15 grants Entitlement
```

## Product mapping

T14 does not hard-code business rules for Free/99/599/1,999/5,999. The `product_id` on an order is the bridge to T12 entitlement rules.

## Future subscription support

The schema intentionally keeps provider references and payment status separate from product entitlement. Future recurring billing can add subscription records/events without changing the order/payments contract.
