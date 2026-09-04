Astro-Zodiac T15 — Payment → Entitlement Integration

Files:
- product_schema.py
- product_catalog.py
- entitlement_engine.py
- membership_schema.py
- membership_service.py
- payment_schema.py
- payment_engine.py
- payment_entitlement_integration.py
- tests/test_payment_entitlement_integration.py
- T15_PAYMENT_ENTITLEMENT_CONTRACT.md
- CHANGELOG_T15.md

T15 links T14 payment success/refund events to T13 membership grants.
It is provider-neutral and keeps T12 as the feature entitlement authority.

Expected downstream flow:
T13 Auth/Membership → T14 Payment/Order → T15 Grant/Revoke → T12 Access Decision → T16 API/Application Integration
