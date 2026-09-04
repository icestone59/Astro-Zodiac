# ASTRO-ZODIAC T19 — PostgreSQL Runtime Integration v1

## Objective
Wire T18 HTTP API to T17 PostgreSQL persistence while keeping T12–T16 domain/application boundaries intact.

## Runtime
`ASTRO_ZODIAC_PERSISTENCE=postgres` selects PostgreSQL. `DATABASE_URL` is required.
Without the setting, local development uses the existing in-memory adapter explicitly.

## Auth persistence
T13 `AuthRepository` is implemented by `PostgresAuthRepository`.
Password hashes are stored; plaintext passwords are never stored. Session tokens are stored only as hashes.

## Membership persistence
T12/T13 active membership grants are read from `membership_grants` and converted to `MembershipState`.

## Security
- API does not trust client product ownership.
- Entitlement is computed from server-side membership state.
- Payment status remains owned by T14/T15.
- No card data is stored.
- User-controlled SQL values use parameters.

## Migration
Run `migrations/002_auth_runtime.sql` after T17 baseline migration and before enabling PostgreSQL persistence.

## Non-goals
- No payment provider SDK.
- No 5,999 semantics.
- No production secret values in the repository.
- No removal of legacy SQLite yet.
