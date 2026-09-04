"""Astro-Zodiac T9 — Psychology Engine contracts.

Psychology features are for self-development. They are not diagnosis or treatment.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple

@dataclass(frozen=True)
class EvidenceSource:
    source_id: str
    title: str
    tier: str
    url: str
    usage_note: str

@dataclass(frozen=True)
class InterventionMethod:
    intervention_id: str
    name: str
    purpose: str
    steps: Tuple[str, ...]
    measurement: Tuple[str, ...]
    source_ids: Tuple[str, ...]
    safety_rules: Tuple[str, ...]

@dataclass(frozen=True)
class WorksheetDefinition:
    worksheet_id: str
    title: str
    fields: Tuple[str, ...]

@dataclass(frozen=True)
class PsychologyRecommendation:
    pattern_id: str
    primary_intervention_id: str
    intervention_ids: Tuple[str, ...]
    worksheet_ids: Tuple[str, ...]
    measurement: Tuple[str, ...]
    safety_rules: Tuple[str, ...]
    evidence_source_ids: Tuple[str, ...]
    rationale: str

@dataclass(frozen=True)
class PsychologyContext:
    pattern_id: str
    validation_status: str
    pattern_fit_score: float

@dataclass
class PsychologyEngineResult:
    recommendation: PsychologyRecommendation
    intervention: InterventionMethod
    worksheets: Tuple[WorksheetDefinition, ...]
    warnings: list[str] = field(default_factory=list)
