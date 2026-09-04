"""Astro-Zodiac T7 — Evidence Snapshot contracts.

Evidence is a deterministic translation layer between Pattern Signals and
report/AI consumers. It stores traceable facts and never invents interpretation.
"""
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


EvidenceDomain = Literal["western", "uranian", "context"]
EvidenceType = Literal[
    "aspect",
    "house_context",
    "house_ruler",
    "sign_context",
    "planetary_picture",
    "90_degree_structure",
    "supportive_aspect",
    "agency_context",
]


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    pattern_id: str
    signal_id: str
    domain: EvidenceDomain
    type: EvidenceType
    statement: str = Field(min_length=1)
    source_refs: List[str] = Field(default_factory=list)
    factors: List[str] = Field(default_factory=list)
    weight: float = Field(ge=0)
    orb: Optional[float] = Field(default=None, ge=0)


class PatternEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pattern_id: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    evidence_count: int = Field(ge=0)
    evidence_weight_total: float = Field(ge=0)
    domains_present: List[EvidenceDomain] = Field(default_factory=list)


class EvidenceSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    engine_version: str = "t7.1"
    source_pattern_engine_version: str
    pattern_library_version: str
    chart_schema_version: str
    patterns: List[PatternEvidence] = Field(default_factory=list)
