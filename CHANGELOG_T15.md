# CHANGELOG — T15

## T15 — Payment → Entitlement Integration

### Added
- `payment_entitlement_integration.py`
- Payment-success → MembershipGrant adapter
- Refund → linked MembershipGrant revoke flow
- Order-scoped idempotency via `external_reference`
- Active product rebuild after revoke
- Integration tests
- T15 contract document

### Design notes
- T12 remains the feature-level entitlement authority.
- T13 owns product membership/ownership state.
- T14 owns payment/order/webhook state.
- Provider-specific details stay outside this module.
- 5,999 remains intentionally out of the product catalog until its design is finalized.
