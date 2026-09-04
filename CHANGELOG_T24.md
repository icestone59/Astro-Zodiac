# CHANGELOG — T24

- Added Vercel FastAPI ASGI entrypoint at `api/index.py`.
- Added explicit Python 3.12 runtime configuration.
- Consolidated runtime requirements and added `email-validator` and `psycopg`.
- Added Vercel environment/deployment contract and setup guide.
- Kept deployment as Preview-first; Production switch is deferred until
  PostgreSQL persistence is verified on Vercel.
