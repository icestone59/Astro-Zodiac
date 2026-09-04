# CHANGELOG — T14

## T14 Payment / Order / Webhook Engine

- Added provider-neutral `Money`, `Order`, `Payment`, `WebhookEvent`, and webhook record contracts.
- Added deterministic order/payment state transitions.
- Added webhook idempotency by `event_id`.
- Added generic HMAC-SHA256 verification helper.
- Kept entitlement granting outside T14; successful payment is handed off to the next integration phase.
- No gateway SDK or secret keys included.

### Validation

Local test suite: 5/5 passed.
