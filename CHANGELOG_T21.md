# CHANGELOG — T21

## T21.1
- Added production runtime configuration validation.
- Made PostgreSQL mandatory when `ASTRO_ZODIAC_ENV=production`.
- Added startup fail-fast behavior for invalid production persistence.
- Added unsupported-mode rejection.
- Updated FastAPI runtime to use the T19 persistence factory for all auth and membership paths.
- Kept memory persistence available only for explicit development/testing.
