# T20 — Render PostgreSQL Runtime Setup

T20 turns the committed T17 PostgreSQL preparation into a repeatable Render runtime procedure.

## Required environment
- `DATABASE_URL` — Render PostgreSQL Internal Database URL
- `ASTRO_ZODIAC_PERSISTENCE=postgres`
- Existing application secrets remain environment variables.

## Build dependency
Add to the deployment requirements:

```text
psycopg[binary]>=3.2,<4
```

## Start command

```bash
bash render_start.sh
```

The wrapper applies pending migrations before starting FastAPI.

## Important migration rule
The SQL files in this T20 package are placeholders by design. **Do not commit them over the T17 migrations.** In the Repo, keep the already-committed T17 files as the authoritative migration source and use those files in the migration runner.

## Render setup
1. Create Render PostgreSQL.
2. Add its Internal Database URL as `DATABASE_URL` on the Web Service.
3. Set `ASTRO_ZODIAC_PERSISTENCE=postgres`.
4. Add psycopg dependency.
5. Set Start Command to `bash render_start.sh` after copying the exact T17 migration SQL into this package's `migrations/` directory, or point the runner at the repo migration directory.
6. Deploy.
7. Verify `/health`, register, login, `/me`, and entitlement API.

## Safety
- Never commit `DATABASE_URL`.
- No destructive `DROP TABLE` migration in T20.
- SQLite remains legacy until a later retirement task.
- PostgreSQL becomes the persistence source only when `ASTRO_ZODIAC_PERSISTENCE=postgres`.
