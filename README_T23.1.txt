Astro-Zodiac T23.1 — Supabase Auth/Entitlement Smoke Test

Run against Astro-Zodiac-DEV after T22.1 migration has been pushed.

Required:
  DATABASE_URL=<Supabase PostgreSQL connection string>

Command:
  python .\t23_1_supabase_auth_entitlement_smoke.py

Do not commit or paste DATABASE_URL into GitHub.
The test cleans up its test user/session/membership by default.
