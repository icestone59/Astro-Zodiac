Astro-Zodiac T17 — PostgreSQL Integration

New files:
- migrations/001_initial_postgres.sql
- postgres_connection.py
- postgres_repository.py
- requirements-t17.txt
- T17_POSTGRES_INTEGRATION_CONTRACT.md
- CHANGELOG_T17.md
- README_T17.txt
- tests/test_t17_contract.py

Important:
T17 prepares PostgreSQL persistence. It does not replace database.py yet.
At deployment time, install requirements-t17.txt and set DATABASE_URL.
