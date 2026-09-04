Astro-Zodiac T24.2 — Vercel PostgreSQL Runtime Fix

Copy:
  postgres_auth_repository.py
  tests/test_t24_2_auth_repository.py
  T24.2_VERCEL_POSTGRES_FIX.md
  CHANGELOG_T24.2.md
  README_T24.2.txt

Then commit and redeploy the Vercel Preview.

After deploy:
  1. Re-run /health.
  2. Register a new unique test account.
  3. Login with the same credentials.
  4. Use the returned bearer token on GET /api/v1/me.
  5. Then test the entitlement endpoint.

Do not reuse a prior test email because it may already exist in Supabase.
