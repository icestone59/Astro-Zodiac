Astro-Zodiac T19 — PostgreSQL Runtime Integration

Production-like mode:
    ASTRO_ZODIAC_PERSISTENCE=postgres
    DATABASE_URL=postgresql://...
    uvicorn api_app:app --host 0.0.0.0 --port 8000

Before enabling postgres:
    1) Apply T17 migrations/001_initial_postgres.sql
    2) Apply T19 migrations/002_auth_runtime.sql
    3) Install requirements-t17.txt + requirements-t18.txt

Local development may omit ASTRO_ZODIAC_PERSISTENCE and use the explicit in-memory adapter.

Do not delete legacy database.py in this milestone.
