Astro-Zodiac T18 — Real HTTP API Adapter

New:
- api_app.py
- T18_API_ADAPTER_CONTRACT.md
- CHANGELOG_T18.md
- README_T18.txt
- tests/test_api_app.py

Run locally:
    uvicorn api_app:app --reload

Before production, replace the in-memory auth/membership adapters with the
T17 PostgreSQL-backed repositories and wire the real payment/webhook adapter.
