from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class BirthChartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year_buddhist: int = Field(ge=1, le=3000)
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    location_name: str = Field(default="กรุงเทพมหานคร", min_length=1, max_length=120)

class PatternAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chart: object
    pattern_result: object
    evidence_snapshot: object

class AccessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allowed: bool
    product_id: str
    feature: str
    reason: str
    ai_remaining: Optional[int] = None

class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    email: str
    display_name: str
    role: str
    status: str
    product_ids: list[str] = Field(default_factory=list)
