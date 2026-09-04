Astro-Zodiac T20 — Render PostgreSQL Runtime

Purpose:
Make the T17 PostgreSQL layer deployable on Render with a safe migration-first startup.

Important:
The repo's committed T17 migrations remain authoritative. This T20 package deliberately does not duplicate or rewrite the SQL schema.

Files:
- migration_runner.py
- render_start.sh
- T20_RENDER_RUNTIME_CONTRACT.md
- CHANGELOG_T20.md
- README_T20.txt
- requirements-t20.txt
- tests/test_t20_contract.py
