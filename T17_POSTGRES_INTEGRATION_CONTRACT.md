# ASTRO-ZODIAC T17 — PostgreSQL Integration Contract v1

## Objective

Introduce PostgreSQL as the persistent production database without deleting or
rewriting the legacy SQLite implementation yet.

## Responsibilities

- `migrations/001_initial_postgres.sql`: baseline relational schema.
- `postgres_connection.py`: `DATABASE_URL` + psycopg connection boundary.
- `postgres_repository.py`: parameterized SQL for core user/billing/usage writes.
- T12–T15 remain owners of product, entitlement, payment, and membership rules.
- T16 remains the application orchestration layer.

## Stored snapshots

Chart and analysis tables store JSONB snapshots plus explicit version fields so
historical results can be reproduced even after engine changes.

## Security

- No passwords or card data are stored by T17 repositories.
- SQL uses parameters; no string interpolation for user-controlled values.
- `DATABASE_URL` is an environment secret.
- User ownership remains enforced above persistence and by foreign keys.

## Compatibility

T17 does not modify `database.py` or the legacy `astro_cache.db`. During the
migration period, new PostgreSQL-backed services should be introduced behind
an adapter and traffic switched gradually.

## Non-goals

- No FastAPI/Flask route changes.
- No payment provider SDK.
- No production migration execution in CI.
- No 5,999 product semantics.
- No business logic in SQL triggers.
