Astro-Zodiac T22 — Real PostgreSQL Smoke Test

Run:
  set DATABASE_URL=postgresql://...
  python t22_smoke_test.py

Linux/macOS:
  DATABASE_URL='postgresql://...' python t22_smoke_test.py

This test must be run against a real PostgreSQL database. In this build
environment no shared Render database credentials are available, so the
package does not claim a live Render smoke test was executed here.
