# Astro-Zodiac T15 — Payment → Entitlement Integration Contract v1

## Purpose
Connect T14 payment/order state to T13 product ownership while keeping T12 as the feature-level entitlement authority.

## Flow
```text
T14 Order / Payment
        ↓
verified successful payment
        ↓
T15 integration
        ↓
T13 MembershipGrant
        ↓
T12 Entitlement check
```

## Rules
1. Only a paid order with a succeeded payment may grant a paid product.
2. `free` must not be granted from a payment event.
3. Granting is idempotent by `order_id` / `external_reference`.
4. A refund revokes only the grant linked to that order; it must not revoke another purchase of the same product.
5. Frontend state is never authoritative for payment or access.
6. Webhook verification and provider-specific parsing remain in T14 adapters / API layer.
7. Subscription renewal/cancellation can be added later without changing this core contract.
8. No card/payment instrument data is stored here.

## Non-scope
- Real payment gateway SDK
- PostgreSQL persistence
- HTTP routes
- Auth UI
- Subscription billing provider implementation
- 5,999 product definition

## Integration examples
- 99 / 599 / 1,999 successful purchase → creates a `MembershipGrant`.
- Duplicate webhook/payment processing → returns the existing grant without duplication.
- Refund → revokes only the grant tied to the refunded order.
