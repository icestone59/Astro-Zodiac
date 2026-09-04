Astro-Zodiac T24.3 — Swagger Bearer Auth

This package adds the FastAPI OpenAPI security scheme required for Swagger
UI to display `Authorize`.

Integration:
  from api_security import extract_bearer_token
  from fastapi import Depends

  token: str = Depends(extract_bearer_token)

The route should then pass `token` to the existing session resolver.

After commit and Vercel redeploy:
  1. Open /docs.
  2. `Authorize` should appear.
  3. Paste the login access token.
  4. Call GET /api/v1/me.
  5. Expect 200 with the authenticated user.
