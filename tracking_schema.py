"""Astro-Zodiac T11 — deterministic tracking contracts.

Tracks observable self-development activity around a T10 action plan.
These metrics are product indicators, not clinical or psychometric scores.
"""
from __future__ import annotations

from typing import Literal, Optional, List
from pydantic import BaseModel, ConfigDict, Field

CheckinStatus = Literal["completed", "partial", "not_completed"]
FailureReason = Literal[
    "too_difficult",
    "forgot",
    "low_energy",
    "unexpected_event",
    "not_important_enough",
    "other",
]
AdjustmentType = Literal[
    "make_it_smaller",
    "change_timing",
    "change_environment",
    "change_trigger",
    "change_worksheet",
]


class BaselineMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    awareness: int = Field(ge=1, le=10)
    confidence: int = Field(ge=1, le=10)
    outcome: int = Field(ge=1, le=10)


class DailyCheckin(BaseModel):
    model_config = ConfigDict(extra="forbid")
    checkin_id: str
    plan_id: str
    day: int = Field(ge=1, le=30)
    status: CheckinStatus
    difficulty: int = Field(ge=1, le=10)
    confidence: int = Field(ge=1, le=10)
    reflection: Optional[str] = Field(default=None, max_length=1000)
    outcome: Optional[int] = Field(default=None, ge=1, le=10)
    failure_reason: Optional[FailureReason] = None


class WeeklyReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: str
    plan_id: str
    period_start_day: int = Field(ge=1, le=30)
    period_end_day: int = Field(ge=1, le=30)
    what_worked: str = Field(min_length=1, max_length=1000)
    what_blocked: str = Field(min_length=1, max_length=1000)
    pattern_when: str = Field(min_length=1, max_length=1000)
    helpful_intervention: str = Field(min_length=1, max_length=1000)
    next_week_change: str = Field(min_length=1, max_length=1000)


class PlanAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    adjustment_id: str
    plan_id: str
    day: int = Field(ge=1, le=30)
    adjustment_type: AdjustmentType
    reason: str
    target_step_id: Optional[str] = None


class ProgressMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    awareness: float = Field(ge=0, le=100)
    behavior: float = Field(ge=0, le=100)
    consistency: float = Field(ge=0, le=100)
    outcome: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)
    completed_checkins: int = Field(ge=0)
    scheduled_checkins: int = Field(ge=0)
    completed_actions: int = Field(ge=0)
    scheduled_actions: int = Field(ge=0)


class CompletionSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_id: str
    completed: bool
    before: BaselineMetrics
    after: BaselineMetrics
    change_awareness: float
    change_confidence: float
    change_outcome: float
    final_reflection: str = Field(min_length=1, max_length=2000)


class TrackingSession(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "1.0"
    engine_version: str = "t11.1"
    plan_id: str
    pattern_id: str
    duration_days: int = Field(ge=7, le=30)
    checkins: List[DailyCheckin] = Field(default_factory=list)
    weekly_reviews: List[WeeklyReview] = Field(default_factory=list)
    adjustments: List[PlanAdjustment] = Field(default_factory=list)
    baseline: Optional[BaselineMetrics] = None
    progress: Optional[ProgressMetrics] = None
    completion: Optional[CompletionSnapshot] = None
