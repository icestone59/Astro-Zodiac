from psychology_engine import recommend_psychology
from psychology_schema import PsychologyContext


def test_validated_p01_returns_intervention_and_worksheet():
    result = recommend_psychology(PsychologyContext("P01", "validated", 82.0))
    assert result.recommendation.primary_intervention_id == "I01"
    assert result.recommendation.worksheet_ids == ("W01", "W02")
    assert "SRC_WOOP" in result.recommendation.evidence_source_ids


def test_unvalidated_pattern_is_blocked():
    try:
        recommend_psychology(PsychologyContext("P02", "explored", 55.0))
    except ValueError as exc:
        assert "validated pattern" in str(exc)
    else:
        raise AssertionError("Expected validation gate")


def test_safety_and_nonclinical_language_present():
    result = recommend_psychology(PsychologyContext("P08", "validated", 76.0))
    assert any("not a diagnosis" in rule.lower() for rule in result.recommendation.safety_rules)
