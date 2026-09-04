# T24 — Vercel Deployment Guide

## A. Import repository

1. Go to Vercel Dashboard.
2. `Add New...` → `Project`.
3. Import `icestone59/Astro-Zodiac`.
4. Keep the Root Directory as the repository root.
5. Framework preset can remain `Other`/auto-detected because `vercel.json`
   defines the Python function.

Vercel supports FastAPI through its Python runtime and the `api/index.py`
ASGI entrypoint pattern. See:
https://vercel.com/kb/fastapi

## B. Environment variables

In Vercel Project Settings → Environment Variables, add:

```text
DATABASE_URL
ASTRO_ZODIAC_ENV=development
ASTRO_ZODIAC_PERSISTENCE=postgres
```

Use the Supabase DEV connection string. Do not paste secrets into GitHub.

Vercel environment variables are scoped to Development/Preview/Production and
require a redeploy to take effect.

## C. Deploy

Start with a Preview deployment.

After the build finishes, open:

```text
https://<your-project>.vercel.app/health
```

Expected:

```json
{
  "status": "ok",
  "pipeline_version": "..."
}
```

## D. Do not switch Production yet

First prove:

1. Build works.
2. `/health` works.
3. FastAPI function starts.
4. Vercel can reach Supabase DEV.
5. Authentication/entitlement runtime is using PostgreSQL rather than memory.

Only then should the Production project/env be configured.

## Sources

- FastAPI on Vercel:
  https://vercel.com/kb/fastapi
- Python starter/runtime:
  https://vercel.com/academy/python-on-vercel
- Environment variables:
  https://vercel.com/academy/vercel-foundations/vercel-settings
