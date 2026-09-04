"""Astro-Zodiac T9 — deterministic Psychology Recommendation Engine."""
from __future__ import annotations
from psychology_library import INTERVENTIONS, PATTERN_MAP, SOURCES, WORKSHEETS
from psychology_schema import PsychologyContext, PsychologyEngineResult, PsychologyRecommendation

SUPPORTED = frozenset(PATTERN_MAP)


def recommend_psychology(context: PsychologyContext) -> PsychologyEngineResult:
    if context.pattern_id not in SUPPORTED:
        raise ValueError(f"Unsupported MVP psychology pattern: {context.pattern_id}")
    if context.validation_status != "validated":
        raise ValueError("Psychology intervention recommendations require a validated pattern")

    primary, alternatives, worksheet_ids = PATTERN_MAP[context.pattern_id]
    intervention = INTERVENTIONS[primary]
    source_ids = tuple(dict.fromkeys(intervention.source_ids + tuple(s for iid in alternatives for s in INTERVENTIONS[iid].source_ids)))
    measurement = tuple(dict.fromkeys(intervention.measurement))
    safety = tuple(dict.fromkeys(intervention.safety_rules + ("This is a self-development recommendation, not a diagnosis or treatment.",)))
    recommendation = PsychologyRecommendation(
        pattern_id=context.pattern_id,
        primary_intervention_id=primary,
        intervention_ids=(primary,) + tuple(i for i in alternatives if i != primary),
        worksheet_ids=worksheet_ids,
        measurement=measurement,
        safety_rules=safety,
        evidence_source_ids=source_ids,
        rationale="Recommendation is based on the validated product pattern and the curated psychology evidence library; it does not infer a clinical condition or claim that astrology caused the pattern.",
    )
    worksheets = tuple(WORKSHEETS[w] for w in worksheet_ids)
    warnings = [SOURCES["SRC_WHO"].usage_note]
    return PsychologyEngineResult(recommendation, intervention, worksheets, warnings)
