"""Astro-Zodiac T8 — Validation Engine contracts.

MVP product scoring only. This is not a psychometric validity score and does
not diagnose mental-health conditions.
"""
from __future__ import annotations

from typing import Literal, List, Optional
from pydantic import BaseModel, ConfigDict, Field

ResponseType = Literal["frequency", "agreement", "behavioral_example"]
PatternFit = Literal["low", "moderate", "strong"]
ValidationStatus = Literal["validated", "explored", "not_confirmed"]


class ValidationQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    pattern_id: str
    text: str
    response_type: ResponseType
    reverse_scored: bool = False
    required: bool = True
    source_kind: Literal["custom_mvp"] = "custom_mvp"


class QuestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    value: Optional[int] = Field(default=None, ge=1, le=5)
    text: Optional[str] = None


class BehavioralEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: str
    strength: float = Field(ge=0, le=1)
    description: Optional[str] = None
    source: Literal["user_report", "behavioral_example"] = "user_report"


class ValidationScores(BaseModel):
    model_config = ConfigDict(extra="forbid")
    astrology_signal_score: float = Field(ge=0, le=30)
    self_report_score: float = Field(ge=0, le=35)
    behavioral_evidence_score: float = Field(ge=0, le=35)
    pattern_fit_score: float = Field(ge=0, le=100)


class PatternValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pattern_id: str
    status: ValidationStatus
    fit: PatternFit
    scores: ValidationScores
    response_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    behavioral_example_present: bool = False
    next_route: str


class ValidationSession(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "1.0"
    engine_version: str = "t8.1"
    pattern_id: str
    questions: List[ValidationQuestion] = Field(default_factory=list)
    responses: List[QuestionResponse] = Field(default_factory=list)
    behavioral_evidence: List[BehavioralEvidence] = Field(default_factory=list)
    result: Optional[PatternValidation] = None
