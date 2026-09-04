Astro-Zodiac T24.3.2 — Global Swagger Authorize

Replace/commit:
- api_app.py
- existing api_security.py if present
- documentation files
- test file

After Vercel redeploy:
1. Open /docs.
2. Confirm `Authorize` at the top.
3. Login and get a fresh access token.
4. Click Authorize and enter the token.
5. Call GET /api/v1/me.
6. Expect 200.
