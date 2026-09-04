from __future__ import annotations
from typing import Annotated
from uuid import UUID
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from application_schema import BirthChartRequest
from application_service import analyze_free, pipeline_version
from auth_service import AuthError, authenticate, create_session, register, resolve_session
from entitlement_engine import check_access
from in_memory_auth_repository import InMemoryAuthRepository
from membership_schema import MembershipState

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
class EntitlementResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allowed: bool
    product_id: str
    feature: str
    reason: str
    ai_remaining: int | None = None

app = FastAPI(title="Astro-Zodiac API", version="0.1.0")
auth_repo = InMemoryAuthRepository()

def _membership_for(user_id: UUID) -> MembershipState:
    return MembershipState(user_id=user_id)

def current_user(authorization: Annotated[str | None, Header()] = None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    token = authorization.split(" ", 1)[1].strip()
    user = resolve_session(auth_repo, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired session")
    return user

@app.get("/health")
def health():
    return {"status": "ok", "pipeline_version": pipeline_version()}
@app.post("/api/v1/auth/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
def api_register(payload: RegisterRequest):
    try:
        user = register(auth_repo, str(payload.email), payload.password, payload.display_name)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return MeResponse(user_id=user.user_id, email=str(user.email), display_name=user.display_name, role=user.role, status=user.status)
@app.post("/api/v1/auth/login", response_model=AuthResponse)
def api_login(payload: LoginRequest):
    try:
        user = authenticate(auth_repo, str(payload.email), payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from exc
    return AuthResponse(user_id=user.user_id, access_token=create_session(auth_repo, user.user_id))
@app.get("/api/v1/me", response_model=MeResponse)
def api_me(user=Depends(current_user)):
    return MeResponse(user_id=user.user_id, email=str(user.email), display_name=user.display_name, role=user.role, status=user.status)
@app.post("/api/v1/analysis/free")
def api_free_analysis(payload: BirthChartRequest, user=Depends(current_user)):
    return analyze_free(payload).model_dump(mode="json")
@app.get("/api/v1/entitlements/{feature}", response_model=EntitlementResponse)
def api_entitlement(feature: str, user=Depends(current_user)):
    decision = check_access(_membership_for(user.user_id).model_copy(), feature)
    return EntitlementResponse(allowed=decision.allowed, product_id=decision.product_id, feature=feature, reason=decision.reason, ai_remaining=decision.ai_remaining)
