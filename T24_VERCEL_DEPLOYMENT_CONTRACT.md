# ASTRO-ZODIAC T24 — Vercel Deployment Contract v1

## Objective

Deploy the existing FastAPI application to Vercel's Python runtime without
moving domain logic.

## Target

```text
GitHub
  ↓
Vercel
  ↓
api/index.py
  ↓
api_app.app (FastAPI)
  ↓
Application / Domain Engines
  ↓
Supabase PostgreSQL
```

## Deployment boundary

- `api/index.py` is the Vercel entrypoint.
- `api_app.py` remains the application FastAPI object.
- Domain engines remain unchanged.
- Supabase is the runtime database.
- No Render dependency is introduced.

## Python runtime

Vercel's current Python runtime supports Python 3.12+; this package explicitly
selects 3.12 for the first deployment test.

## Required environment variables

For the first DEV deployment:

```text
DATABASE_URL=<Supabase DEV connection string>
ASTRO_ZODIAC_ENV=development
ASTRO_ZODIAC_PERSISTENCE=postgres
```

Do not commit secrets.

## Important current limitation

The current committed `api_app.py` still imports
`InMemoryAuthRepository` directly. T24 therefore verifies that the FastAPI app
can deploy, but **does not claim production-grade persistent Auth on Vercel**
until the T19/T21.1 persistence wiring is audited against the actual committed
files.

## Done when

- Vercel project imports GitHub repo.
- Build/install succeeds.
- `/health` returns 200.
- Python function logs show successful startup.
- A protected endpoint is reachable.
- Database access is tested in a later step after the Vercel environment
  variables are configured.
