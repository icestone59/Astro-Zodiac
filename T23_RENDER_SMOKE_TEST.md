# ASTRO-ZODIAC T23 — Render PostgreSQL Smoke Test

## Goal

Run the exact T22 PostgreSQL smoke test against the real Render PostgreSQL
database before connecting the live application to customer traffic.

## Render connection

For a Render-hosted Web Service and Render Postgres in the same region,
prefer the database **Internal Database URL**. Render documents that internal
connections stay on the private network; external URLs are for clients
outside Render and require TLS. See Render docs:
https://render.com/docs/postgresql-creating-connecting

## Render setup

On the local machine, use the database's **External Database URL** to smoke
test Render from outside Render:

```powershell
$env:DATABASE_URL="postgresql://USER:PASSWORD@HOST/DB?sslmode=require"
python t22_smoke_test.py
```

On the Render Web Service itself, set:

```text
DATABASE_URL=<Render Internal Database URL>
ASTRO_ZODIAC_ENV=production
ASTRO_ZODIAC_PERSISTENCE=postgres
```

Never commit DATABASE_URL or any database password into Git.

## Success criteria

All of these must pass:

1. PostgreSQL connection succeeds.
2. Migrations 001 + 002 succeed.
3. Required auth/membership columns exist.
4. User row can be inserted.
5. Session row can be inserted.
6. Membership grant can be inserted.
7. Membership grant can be read back.
8. Test data is cleaned up.

## Important

This package does NOT claim the shared Render database has already been tested.
The actual smoke test requires the user's DATABASE_URL.

After the smoke test passes, the next production step is to wire the Render
Web Service to the database and run the API health/auth smoke flow.
