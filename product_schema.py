"""Astro-Zodiac T12 — product and entitlement contracts."""
from __future__ import annotations

from typing import Dict, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

ProductId = Literal["free", "personal_insight_99", "action_plan_599", "astro_professional_1999"]
FeatureId = Literal[
    "free_discovery",
    "pattern_top3",
    "full_pattern_evidence",
    "pattern_validation",
    "ai_personal_insight",
    "psychology_intervention",
    "action_plan",
    "tracking",
    "ai_life_planning",
    "natal_full",
    "house_ruler",
    "aspects",
    "uranian_full",
    "transit_analysis",
    "evidence_matrix",
    "deep_report",
    "client_history",
    "report_export",
]


class AIQuota(BaseModel):
    model_config = ConfigDict(extra="forbid")
    questions: Optional[int] = Field(default=None, ge=0)
    unit: Literal["question"] = "question"


class EntitlementSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: ProductId
    features: Dict[FeatureId, bool]
    ai_quota: AIQuota


class UserProductState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active_products: list[ProductId] = Field(default_factory=lambda: ["free"])


class AccessDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allowed: bool
    product_id: ProductId
    feature: FeatureId
    reason: str
    ai_remaining: Optional[int] = None
