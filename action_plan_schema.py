"""Astro-Zodiac T10 — Action Plan contracts.

Converts a validated pattern + T9 psychology recommendation into a finite,
deterministic self-development plan. This is not diagnosis or treatment.
"""
from __future__ import annotations

from typing import Literal, List, Optional
from pydantic import BaseModel, ConfigDict, Field

PlanDuration = Literal[7, 14, 30]
ActionType = Literal["reflection", "practice", "real_world", "check_in", "review"]


class GoalContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal_statement: str = Field(min_length=3, max_length=500)
    reason: Optional[str] = Field(default=None, max_length=500)
    preferred_duration_days: PlanDuration = 14


class ActionStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step_id: str
    day: int = Field(ge=1, le=30)
    title: str
    action: str
    action_type: ActionType
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=180)
    worksheet_id: Optional[str] = None
    measurement_id: Optional[str] = None
    completion_required: bool = True


class ActionPhase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phase_id: str
    title: str
    purpose: str
    days: List[int] = Field(min_length=1)
    steps: List[ActionStep] = Field(min_length=1)


class ProgressCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    check_id: str
    day: int = Field(ge=1, le=30)
    prompt: str
    metric_ids: List[str] = Field(default_factory=list)


class ActionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "1.0"
    engine_version: str = "t10.1"
    pattern_id: str
    validation_status: Literal["validated"] = "validated"
    primary_intervention_id: str
    worksheet_ids: List[str] = Field(default_factory=list)
    duration_days: PlanDuration
    goal: GoalContext
    phases: List[ActionPhase] = Field(min_length=1)
    progress_checks: List[ProgressCheck] = Field(default_factory=list)
    measurement_ids: List[str] = Field(default_factory=list)
    safety_rules: List[str] = Field(default_factory=list)
    next_route: Literal["tracking"] = "tracking"
