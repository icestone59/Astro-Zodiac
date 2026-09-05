from __future__ import annotations
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, status
from api_security import extract_bearer_token
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from application_schema import BirthChartRequest
from application_service import analyze_free, pipeline_version
from auth_service import AuthError, authenticate, create_session, register, resolve_session
from entitlement_engine import check_access
from membership_schema import MembershipState
from product_schema import UserProductState
from persistence_factory import auth_repository, membership_repository
from runtime_config import persistence_mode, validate_runtime_config

class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    display_name: str = Field(default="", max_length=120)
class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
class AuthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    access_token: str
    token_type: str = "bearer"
class MeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    email: str
    display_name: str
    role: str
    status: str
    active_products: list[str]
class EntitlementResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allowed: bool
    product_id: str
    feature: str
    reason: str
    ai_remaining: int | None = None

app = FastAPI(
    title="Astro-Zodiac API",
    version="0.3.0",
    openapi_version="3.1.0",
)


def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version="3.1.0",
    )

    schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "BearerAuth"
    ] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "token",
        "description": "Paste the access token returned by POST /api/v1/auth/login.",
    }

    protected_routes = {
        "/api/v1/me",
        "/api/v1/analysis/free",
    }
    # Entitlement is also protected.
    protected_routes.add("/api/v1/entitlements/{feature}")

    for route_path in protected_routes:
        path_item = schema.get("paths", {}).get(route_path, {})
        for operation in path_item.values():
            if isinstance(operation, dict):
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi


def _startup_validate() -> None:
    validate_runtime_config()


# Validate config during import so an incorrectly configured runtime fails fast.
_startup_validate()


def _get_user(token: str = Depends(extract_bearer_token)):
    with auth_repository() as repo:
        user = resolve_session(repo, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def _membership(user_id: UUID) -> MembershipState:
    with membership_repository() as repo:
        return repo.get_state(user_id)

@app.get("/health")
def health():
    validate_runtime_config()
    # connection() itself will raise if the DB is unavailable.
    with auth_repository() as repo:
        # A harmless query through the repository boundary verifies connectivity.
        repo.ping()
    return {"status": "ok", "pipeline_version": pipeline_version(), "persistence": persistence_mode()}

@app.post("/api/v1/auth/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
def api_register(payload: RegisterRequest):
    try:
        with auth_repository() as repo:
            user = register(repo, str(payload.email), payload.password, payload.display_name)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    membership = _membership(user.user_id)
    return MeResponse(user_id=user.user_id, email=str(user.email), display_name=user.display_name,
                      role=user.role, status=user.status, active_products=membership.active_products)

@app.post("/api/v1/auth/login", response_model=AuthResponse)
def api_login(payload: LoginRequest):
    try:
        with auth_repository() as repo:
            user = authenticate(repo, str(payload.email), payload.password)
            token = create_session(repo, user.user_id)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from exc
    return AuthResponse(user_id=user.user_id, access_token=token)

@app.get("/api/v1/me", response_model=MeResponse)
def api_me(user=Depends(_get_user)):
    membership = _membership(user.user_id)
    return MeResponse(user_id=user.user_id, email=str(user.email), display_name=user.display_name,
                      role=user.role, status=user.status, active_products=membership.active_products)

@app.post("/api/v1/analysis/free")
def api_free_analysis(payload: BirthChartRequest, user=Depends(_get_user)):
    return analyze_free(payload).model_dump(mode="json")

@app.get("/api/v1/entitlements/{feature}", response_model=EntitlementResponse)
def api_entitlement(feature: str, user=Depends(_get_user)):
    state = _membership(user.user_id)
    product_state = UserProductState(active_products=state.active_products)
    decision = check_access(product_state, feature)
    return EntitlementResponse(allowed=decision.allowed, product_id=decision.product_id, feature=decision.feature,
                               reason=decision.reason, ai_remaining=decision.ai_remaining)
