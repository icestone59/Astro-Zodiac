Astro-Zodiac T21 — Production Persistence Switch

New/changed:
- api_app.py
- persistence_factory.py
- runtime_config.py
- T21_PRODUCTION_PERSISTENCE_CONTRACT.md
- CHANGELOG_T21.md
- README_T21.txt
- tests/test_t21_runtime_config.py

Before production on Render, set:
ASTRO_ZODIAC_ENV=production
ASTRO_ZODIAC_PERSISTENCE=postgres
DATABASE_URL=<Render PostgreSQL Internal Database URL>

Do not commit DATABASE_URL.
