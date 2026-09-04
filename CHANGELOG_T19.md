# CHANGELOG — T19

## T19.1
- Added PostgreSQL-backed AuthRepository adapter.
- Added PostgreSQL membership-state reader.
- Added persistence runtime selector.
- Added FastAPI app wired to persistent auth/membership when enabled.
- Added migration for password_hash and persistent sessions.
- Kept in-memory mode as explicit local-development fallback.
