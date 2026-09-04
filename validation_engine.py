"""Astro-Zodiac T8 — deterministic Pattern Validation Engine.

Converts user assessment responses + explicit behavioral evidence + the T6
astrology score into an MVP Pattern Fit score. The result is a product score,
not psychometric validity and not a diagnosis.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence

from pattern_schema import PatternCandidate
from validation_question_bank import get_questions
from validation_schema import (
    BehavioralEvidence,
    PatternValidation,
    QuestionResponse,
    ValidationQuestion,
    ValidationScores,
    ValidationSession,
)

MIN_REQUIRED_RESPONSES = 5


def _pattern_questions(pattern_id: str) -> Sequence[ValidationQuestion]:
    return get_questions(pattern_id, limit=8)


def _response_value(question: ValidationQuestion, response: QuestionResponse) -> float:
    if response.value is None:
        return 0.0
    normalized = (response.value - 1) / 4
    return 1.0 - normalized if question.reverse_scored else normalized


def calculate_self_report_score(
    pattern_id: str,
    responses: Sequence[QuestionResponse],
) -> float:
    """Map answered 1–5 items to a 0–35 symptom-alignment product score."""
    questions = {q.question_id: q for q in _pattern_questions(pattern_id)}
    values: List[float] = []
    for response in responses:
        question = questions.get(response.question_id)
        if question is None or question.response_type == "behavioral_example":
            continue
        values.append(_response_value(question, response))
    if not values:
        return 0.0
    return round(sum(values) / len(values) * 35, 4)


def calculate_behavioral_evidence_score(
    behavioral_evidence: Sequence[BehavioralEvidence],
) -> float:
    """Convert explicit user-supplied behavioral evidence strengths to 0–35."""
    if not behavioral_evidence:
        return 0.0
    # Diminishing return avoids double-counting many examples of the same theme.
    strongest = sorted((item.strength for item in behavioral_evidence), reverse=True)
    weighted = 0.0
    weights = (0.60, 0.25, 0.15)
    for strength, weight in zip(strongest, weights):
        weighted += strength * weight
    return round(min(1.0, weighted) * 35, 4)


def _fit_label(total: float) -> str:
    if total < 40:
        return "low"
    if total < 70:
        return "moderate"
    return "strong"


def _status(label: str, *, enough_responses: bool) -> str:
    if not enough_responses:
        return "explored"
    if label == "low":
        return "not_confirmed"
    return "validated"


def validate_pattern(
    candidate: PatternCandidate,
    responses: Sequence[QuestionResponse],
    behavioral_evidence: Sequence[BehavioralEvidence] = (),
    *,
    behavioral_example_text: str | None = None,
) -> PatternValidation:
    """Validate one T6 candidate against user-reported experience."""
    if candidate.pattern_id not in {"P01", "P02", "P03", "P05", "P06", "P08"}:
        raise ValueError(f"Unsupported MVP validation pattern: {candidate.pattern_id}")

    valid_question_ids = {q.question_id for q in _pattern_questions(candidate.pattern_id)}
    scoped_responses = [r for r in responses if r.question_id in valid_question_ids]
    self_report = calculate_self_report_score(candidate.pattern_id, scoped_responses)
    behavioral = calculate_behavioral_evidence_score(behavioral_evidence)
    astrology = min(30.0, max(0.0, candidate.score.total / 10.0 * 30.0))
    total = round(astrology + self_report + behavioral, 4)
    fit = _fit_label(total)
    enough = len([r for r in scoped_responses if r.value is not None]) >= MIN_REQUIRED_RESPONSES
    status = _status(fit, enough_responses=enough)
    example_present = bool((behavioral_example_text or "").strip()) or any(
        item.source == "behavioral_example" for item in behavioral_evidence
    )
    return PatternValidation(
        pattern_id=candidate.pattern_id,
        status=status,
        fit=fit,
        scores=ValidationScores(
            astrology_signal_score=round(astrology, 4),
            self_report_score=self_report,
            behavioral_evidence_score=behavioral,
            pattern_fit_score=total,
        ),
        response_count=len(scoped_responses),
        evidence_count=len(behavioral_evidence),
        behavioral_example_present=example_present,
        next_route=("continue_questions" if not enough else "personal_report"),
    )


def create_validation_session(
    candidate: PatternCandidate,
    *,
    responses: Iterable[QuestionResponse] = (),
    behavioral_evidence: Iterable[BehavioralEvidence] = (),
    behavioral_example_text: str | None = None,
) -> ValidationSession:
    """Build a complete deterministic T8 validation session."""
    session = ValidationSession(
        pattern_id=candidate.pattern_id,
        questions=list(_pattern_questions(candidate.pattern_id)),
        responses=list(responses),
        behavioral_evidence=list(behavioral_evidence),
    )
    session.result = validate_pattern(
        candidate,
        session.responses,
        session.behavioral_evidence,
        behavioral_example_text=behavioral_example_text,
    )
    return session
