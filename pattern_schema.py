"""Astro-Zodiac T6 — Pattern contracts.

Deterministic output only.  No AI interpretation and no psychological diagnosis.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


PatternStatus = Literal["candidate"]
PatternKind = Literal["blind_spot", "secondary", "strength"]
SignalDomain = Literal["western", "uranian", "context"]


class PatternSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signal_id: str
    domain: SignalDomain
    type: str
    source: str
    detail: str
    weight: float = Field(ge=0)
    orb: Optional[float] = Field(default=None, ge=0)
    factors: List[str] = []
    independent_key: Optional[str] = None


class PatternScore(BaseModel):
    model_config = ConfigDict(extra="forbid")
    western: float = Field(ge=0)
    uranian: float = Field(ge=0)
    context: float = Field(ge=0)
    specificity: float = Field(ge=0)
    signal_count: int = Field(ge=0)
    total: float = Field(ge=0)


class PatternCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pattern_id: str
    name: str
    status: PatternStatus = "candidate"
    kind: PatternKind = "blind_spot"
    life_question: str
    score: PatternScore
    signals: List[PatternSignal] = []
    validation_route: str
    language: Literal["pattern_to_explore"] = "pattern_to_explore"


class PatternRanking(BaseModel):
    model_config = ConfigDict(extra="forbid")
    primary: Optional[PatternCandidate] = None
    secondary: Optional[PatternCandidate] = None
    strength: Optional[PatternCandidate] = None
    candidates: List[PatternCandidate] = []


class PatternEngineResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine_version: str = "t6.1"
    pattern_library_version: str = "v1"
    ranking: PatternRanking
