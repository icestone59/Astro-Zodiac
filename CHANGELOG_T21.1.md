# CHANGELOG — T21.1

- Changed runtime persistence policy to PostgreSQL-first / PostgreSQL-only.
- Removed memory fallback from `persistence_factory.py`.
- Made `DATABASE_URL` mandatory for runtime.
- Made `ASTRO_ZODIAC_PERSISTENCE=postgres` mandatory.
- Added database connectivity check to `/health`.
- Kept in-memory repositories only as test doubles.
- No new business logic or 5,999 semantics added.
