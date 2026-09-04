from action_plan_schema import ActionPhase, ActionPlan, ActionStep, GoalContext
from tracking_engine import create_tracking_session, record_checkin, failed_streak, suggest_adaptation, complete_plan
from tracking_schema import BaselineMetrics, DailyCheckin

def plan():
    return ActionPlan(
        pattern_id="P01", primary_intervention_id="I01", worksheet_ids=["W01"], duration_days=7,
        goal=GoalContext(goal_statement="Start important work"),
        phases=[ActionPhase(phase_id="P1", title="Start", purpose="p", days=[1,2,3,4,5,6,7], steps=[
            ActionStep(step_id="S1", day=1, title="Start", action="Do it", action_type="practice")
        ])], progress_checks=[], measurement_ids=["m1"], safety_rules=[]
    )

def test_checkin_validation_and_adaptation():
    s=create_tracking_session(plan(), BaselineMetrics(awareness=4,confidence=4,outcome=4))
    for d in range(1,4):
        s=record_checkin(s, DailyCheckin(checkin_id=f"c{d}",plan_id=s.plan_id,day=d,status="not_completed",difficulty=8,confidence=3,reflection="blocked",failure_reason="too_difficult"))
    assert failed_streak(s)==3
    assert suggest_adaptation(s).adjustment_type=="make_it_smaller"

def test_completion_snapshot():
    s=create_tracking_session(plan(), BaselineMetrics(awareness=4,confidence=4,outcome=4))
    for d in range(1,8):
        s=record_checkin(s, DailyCheckin(checkin_id=f"c{d}",plan_id=s.plan_id,day=d,status="completed",difficulty=4,confidence=7,reflection="done",outcome=7))
    snap=complete_plan(s,BaselineMetrics(awareness=7,confidence=7,outcome=7),"I learned what makes starting easier.")
    assert snap.completed
    assert snap.change_outcome==3

def test_no_adaptation_before_three_failures():
    s=create_tracking_session(plan())
    for d in range(1,3):
        s=record_checkin(s, DailyCheckin(checkin_id=f"c{d}",plan_id=s.plan_id,day=d,status="not_completed",difficulty=8,confidence=3,failure_reason="too_difficult"))
    assert suggest_adaptation(s) is None

def test_plan_id_is_stable():
    assert create_tracking_session(plan()).plan_id=="T10-P01-7D"
