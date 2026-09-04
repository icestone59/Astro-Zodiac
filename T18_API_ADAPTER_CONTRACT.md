# ASTRO-ZODIAC T18 — REAL HTTP API ADAPTER CONTRACT v1

## Objective
Expose the T16 application layer through a thin FastAPI adapter without moving business logic into route handlers.

## Routes
- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- `POST /api/v1/analysis/free`
- `GET /api/v1/entitlements/{feature}`

## Boundaries
- Authentication uses T13 domain service.
- Entitlement uses T12/T15 domain logic.
- Analysis calls T16 application service.
- Astrology calculations remain deterministic.
- Payment provider SDKs are not embedded in routes.
- The shipped adapter starts with the T13 in-memory repository as a development adapter; production must inject the T17 PostgreSQL repository before launch.

## Security
- Protected routes require Bearer authentication.
- Passwords never enter the response.
- Client input is Pydantic-validated.
- Frontend cannot grant entitlement.
- `/health` contains no secrets.

## Non-goals
- No production database wiring in the adapter.
- No payment-provider implementation.
- No AI route yet.
- No frontend changes.
