from action_plan_engine import build_action_plan
from action_plan_schema import GoalContext
from psychology_engine import recommend_psychology
from psychology_schema import PsychologyContext, PsychologyEngineResult, PsychologyRecommendation, InterventionMethod, WorksheetDefinition


def _psych(pattern_id: str):
    return recommend_psychology(PsychologyContext(pattern_id, "validated", 80))


def test_builds_7_day_plan():
    plan = build_action_plan(
        _psych("P01"),
        GoalContext(goal_statement="เริ่มงานสำคัญโดยไม่ผัดวัน", preferred_duration_days=7),
    )
    assert plan.pattern_id == "P01"
    assert plan.duration_days == 7
    assert len(plan.phases) == 3
    assert any(step.action_type == "check_in" for phase in plan.phases for step in phase.steps)


def test_builds_14_day_plan_with_goal_preserved():
    goal = GoalContext(goal_statement="ตัดสินใจเรื่องงานให้เร็วขึ้น", preferred_duration_days=14)
    plan = build_action_plan(_psych("P03"), goal)
    assert plan.duration_days == 14
    assert plan.goal.goal_statement == goal.goal_statement
    assert "plan_review" in plan.measurement_ids


def test_builds_30_day_plan_and_safety():
    plan = build_action_plan(
        _psych("P05"),
        GoalContext(goal_statement="สร้างหลักฐานความสามารถในการทำงาน", preferred_duration_days=30),
    )
    assert plan.duration_days == 30
    assert any("self-development" in rule.lower() for rule in plan.safety_rules)


def test_rejects_unsupported_pattern():
    base = _psych("P01").recommendation
    bad_rec = PsychologyRecommendation(
        pattern_id="P99",
        primary_intervention_id=base.primary_intervention_id,
        intervention_ids=base.intervention_ids,
        worksheet_ids=base.worksheet_ids,
        measurement=base.measurement,
        safety_rules=base.safety_rules,
        evidence_source_ids=base.evidence_source_ids,
        rationale=base.rationale,
    )
    bad_result = PsychologyEngineResult(
        recommendation=bad_rec,
        intervention=_psych("P01").intervention,
        worksheets=_psych("P01").worksheets,
    )
    try:
        build_action_plan(bad_result, GoalContext(goal_statement="test"))
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("Expected unsupported-pattern ValueError")
