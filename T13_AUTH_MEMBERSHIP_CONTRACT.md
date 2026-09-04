# Astro-Zodiac T13 — Auth & Membership Foundation Contract v1

## Purpose
Establish a framework-agnostic foundation for user identity, authentication sessions, and product ownership before billing/payment integration.

## Scope
- User account contract
- User profile contract
- Password hashing/verification primitive
- Opaque session token contract
- Membership plan/grant/state contract
- Ownership checks
- Repository protocol + in-memory test adapter

## Explicit non-scope
- Payment gateway
- Orders/invoices/refunds
- Payment webhooks
- Real PostgreSQL migrations
- HTTP routes/UI
- 5,999 product design
- LINE OA

## Security rules
1. Normalize email before lookup/creation.
2. Never store plaintext passwords.
3. Never persist raw session/reset tokens; persist hashes.
4. Backend remains authoritative for authentication and product ownership.
5. Session resolution checks expiry.
6. Account status is enforced before login.
7. Production password storage should use an established Argon2id implementation; T13's stdlib PBKDF2 implementation is a dependency-light foundation/test primitive.

## Membership rules
- `free` is always available as the baseline product.
- Product ownership is represented by `MembershipGrant` records.
- Payment will later create/modify grants via a controlled adapter.
- Expired/revoked grants must not provide access.
- Do not hard-code product flags inside frontend routes.

## Handoff
```text
T12 Product/Entitlement
        ↓
T13 User/Auth/Membership Foundation
        ↓
T14 Payment/Order/Webhook
        ↓
T15 Payment → Entitlement integration
        ↓
T16 API/Application Integration
```
