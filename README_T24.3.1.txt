Astro-Zodiac T24.3.1 — Swagger Authorize Fix

Copy to repo and commit:
- api_app.py
- api_security.py
- api/index.py
- vercel.json
- tests/test_t24_3_1_source_contract.py
- documentation files

Then redeploy the Vercel Preview.

Expected:
  /docs -> Authorize button
  Login -> access token
  Authorize -> Bearer <token>
  GET /api/v1/me -> 200
