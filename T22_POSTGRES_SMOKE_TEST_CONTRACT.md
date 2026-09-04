# ASTRO-ZODIAC T22 — Real PostgreSQL Smoke Test Contract v1

## Objective

Verify the production persistence path against a real PostgreSQL instance.

This task is an executable smoke-test package, not a claim that the shared
Render database has already been tested. The test requires `DATABASE_URL`.

## Required path

```text
Database URL
    ↓
Migration 001 + 002
    ↓
User creation
    ↓
Session creation
    ↓
Membership grant
    ↓
Entitlement read
    ↓
Cleanup
```

## Rules

- No in-memory repositories are used by the smoke test.
- The database must be PostgreSQL.
- Migrations are applied in order.
- Test data is isolated by unique email and cleaned up at the end.
- Passwords are never printed.
- The test reports actionable failure stages.

## Environment

Required:
`DATABASE_URL=postgresql://...`

Optional:
`T22_KEEP_TEST_DATA=1`

## Local vs Render

Run the same smoke test against:
1. Local development PostgreSQL
2. Render PostgreSQL

The SQL and repository code are therefore exercised against the same DB engine
in both environments.

## Not included

- Payment gateway live charge
- LINE OA
- AI credits
- 5,999 product
- Frontend
