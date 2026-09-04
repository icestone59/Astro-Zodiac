# CHANGELOG — T17

## T17.1
- Added PostgreSQL baseline schema for users, memberships, orders, payments,
  webhooks, charts, analyses, validation, action plans, tracking, and AI usage.
- Added psycopg connection boundary using `DATABASE_URL`.
- Added parameterized PostgreSQL repository for core account/billing/usage flows.
- Preserved the existing SQLite layer; no destructive migration performed.
