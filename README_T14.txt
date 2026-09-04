Astro-Zodiac T14 — Payment / Order / Webhook

Files
- payment_schema.py
- payment_engine.py
- tests/test_payment_engine.py
- T14_PAYMENT_ORDER_CONTRACT.md
- CHANGELOG_T14.md

Integration rule
Do not connect a frontend success page directly to entitlement. The verified provider webhook must transition Payment -> Order -> downstream entitlement.

T14 is intentionally provider-neutral. Select the actual Thai payment provider/gateway when wiring HTTP routes in the next integration phase.
