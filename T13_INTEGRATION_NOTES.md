# T13 Integration Notes

1. Keep `main.py` as an adapter/orchestrator; do not put auth rules inside routes.
2. A future DB adapter should implement `AuthRepository` and persist users, credential hashes, sessions, and membership grants in PostgreSQL.
3. T12 entitlement checks remain the feature-level authority. T13 only supplies identity + product ownership state.
4. T14 should consume successful payment events and create/update MembershipGrant records.
5. Do not enable or define 5,999 entitlements here; that product remains intentionally unresolved.
