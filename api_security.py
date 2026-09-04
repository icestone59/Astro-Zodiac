"""Astro-Zodiac T24.3 — FastAPI Bearer/OpenAPI security integration."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(
    auto_error=True,
    scheme_name="BearerAuth",
    description="Paste the access token returned by POST /api/v1/auth/login.",
)


def extract_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Return the raw bearer token for the existing session resolver."""
    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
