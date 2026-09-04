# CHANGELOG — T12

## T12.1
- Added `product_schema.py` with explicit product, feature, AI quota, and access contracts.
- Added `product_catalog.py` as the single data-driven MVP entitlement catalog.
- Added `entitlement_engine.py` for server-side feature and AI quota checks.
- Added unit tests for Free / 99 / 599 / 1,999 boundaries.
- Kept Professional AI quota intentionally unlocked pending a separate product decision.
- No payment/auth/persistence wiring in this milestone.
