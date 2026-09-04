"""Astro-Zodiac T11 — deterministic tracking engine."""
from __future__ import annotations

from typing import Iterable, Optional

from action_plan_schema import ActionPlan, ActionStep
from tracking_schema import (
    BaselineMetrics,
    CompletionSnapshot,
    DailyCheckin,
    PlanAdjustment,
    ProgressMetrics,
    TrackingSession,
    WeeklyReview,
)


def make_plan_id(action_plan: ActionPlan) -> str:
    """Create a stable local plan reference from the T10 plan identity fields."""
    return f"T10-{action_plan.pattern_id}-{action_plan.duration_days}D"


def create_tracking_session(
    action_plan: ActionPlan,
    baseline: Optional[BaselineMetrics] = None,
) -> TrackingSession:
    """Initialize an in-memory tracking session for a T10 plan."""
    return TrackingSession(
        plan_id=make_plan_id(action_plan),
        pattern_id=action_plan.pattern_id,
        duration_days=action_plan.duration_days,
        baseline=baseline,
    )


def _scheduled_action_steps(action_plan: ActionPlan) -> list[ActionStep]:
    return [
        step
        for phase in action_plan.phases
        for step in phase.steps
        if step.action_type != "check_in"
    ]


def get_actions_for_day(action_plan: ActionPlan, day: int) -> list[ActionStep]:
    """Return non-check-in T10 action steps assigned to the requested day."""
    if day < 1 or day > action_plan.duration_days:
        raise ValueError("day is outside the action-plan duration")
    return [step for step in _scheduled_action_steps(action_plan) if step.day == day]


def record_checkin(
    session: TrackingSession,
    checkin: DailyCheckin,
) -> TrackingSession:
    """Return a new session with the supplied daily check-in applied."""
    if checkin.plan_id != session.plan_id:
        raise ValueError("check-in plan_id does not match tracking session")
    if checkin.day > session.duration_days:
        raise ValueError("check-in day exceeds plan duration")
    if checkin.status == "not_completed" and not checkin.failure_reason:
        raise ValueError("failure_reason is required when status is not_completed")
    if checkin.status != "not_completed" and checkin.failure_reason:
        raise ValueError("failure_reason is only valid for not_completed check-ins")

    existing = [c for c in session.checkins if c.checkin_id != checkin.checkin_id]
    updated = session.model_copy(update={"checkins": existing + [checkin]})
    return updated.model_copy(update={"progress": calculate_progress(updated)})


def _status_weight(status: str) -> float:
    return {"completed": 1.0, "partial": 0.5, "not_completed": 0.0}[status]


def calculate_progress(session: TrackingSession) -> ProgressMetrics:
    checkins = sorted(session.checkins, key=lambda c: (c.day, c.checkin_id))
    scheduled_checkins = session.duration_days
    completed_checkins = sum(1 for c in checkins if c.status != "not_completed")
    behavior = (
        sum(_status_weight(c.status) for c in checkins) / len(checkins) * 100
        if checkins else 0.0
    )

    # Consistency measures coverage of distinct days, not streak perfection.
    distinct_days = {c.day for c in checkins}
    consistency = min(len(distinct_days) / scheduled_checkins * 100, 100.0)

    awareness_values = [c.confidence for c in checkins if c.reflection]
    awareness = sum(awareness_values) / len(awareness_values) * 10 if awareness_values else 0.0

    outcome_values = [c.outcome for c in checkins if c.outcome is not None]
    if outcome_values:
        outcome = sum(outcome_values) / len(outcome_values) * 10
    elif session.baseline:
        outcome = session.baseline.outcome * 10
    else:
        outcome = 0.0

    overall = (awareness + behavior + consistency + outcome) / 4
    scheduled_actions = 0
    # The engine only sees check-ins here; action-level completion is represented by check-in status.
    # Keep a transparent MVP denominator instead of inventing unobserved action completions.
    completed_actions = round(sum(_status_weight(c.status) for c in checkins))
    scheduled_actions = len(checkins)

    return ProgressMetrics(
        awareness=round(awareness, 2),
        behavior=round(behavior, 2),
        consistency=round(consistency, 2),
        outcome=round(outcome, 2),
        overall=round(overall, 2),
        completed_checkins=completed_checkins,
        scheduled_checkins=scheduled_checkins,
        completed_actions=completed_actions,
        scheduled_actions=scheduled_actions,
    )


def build_weekly_review_prompt(plan_id: str, start_day: int, end_day: int) -> WeeklyReview:
    """Create a blank-but-schema-valid review shell for the UI/API layer."""
    return WeeklyReview(
        review_id=f"{plan_id}-REVIEW-{start_day:02d}-{end_day:02d}",
        plan_id=plan_id,
        period_start_day=start_day,
        period_end_day=end_day,
        what_worked="Describe what worked well.",
        what_blocked="Describe what got in the way.",
        pattern_when="Describe when the pattern showed up.",
        helpful_intervention="Which intervention helped most, and how?",
        next_week_change="What will you change for the next period?",
    )


def add_weekly_review(session: TrackingSession, review: WeeklyReview) -> TrackingSession:
    if review.plan_id != session.plan_id:
        raise ValueError("weekly review plan_id does not match tracking session")
    reviews = [r for r in session.weekly_reviews if r.review_id != review.review_id]
    return session.model_copy(update={"weekly_reviews": reviews + [review]})


def failed_streak(session: TrackingSession) -> int:
    """Count consecutive most-recent not_completed check-ins by day order."""
    if not session.checkins:
        return 0
    ordered = sorted(session.checkins, key=lambda c: (c.day, c.checkin_id), reverse=True)
    streak = 0
    expected_day = ordered[0].day
    for checkin in ordered:
        if checkin.day != expected_day:
            break
        if checkin.status != "not_completed":
            break
        streak += 1
        expected_day -= 1
    return streak


def suggest_adaptation(
    session: TrackingSession,
    target_step_id: Optional[str] = None,
) -> Optional[PlanAdjustment]:
    """After three consecutive failures, recommend a non-judgmental adjustment route."""
    if failed_streak(session) < 3:
        return None
    latest = max(session.checkins, key=lambda c: (c.day, c.checkin_id))
    reason_to_type = {
        "too_difficult": "make_it_smaller",
        "forgot": "change_timing",
        "low_energy": "change_timing",
        "unexpected_event": "change_environment",
        "not_important_enough": "change_trigger",
        "other": "change_worksheet",
    }
    adjustment_type = reason_to_type.get(latest.failure_reason or "other", "change_worksheet")
    return PlanAdjustment(
        adjustment_id=f"{session.plan_id}-ADAPT-{latest.day:02d}",
        plan_id=session.plan_id,
        day=latest.day,
        adjustment_type=adjustment_type,
        reason="The same action was not completed three times in a row; adjust the setup instead of blaming the user.",
        target_step_id=target_step_id,
    )


def add_adjustment(session: TrackingSession, adjustment: PlanAdjustment) -> TrackingSession:
    if adjustment.plan_id != session.plan_id:
        raise ValueError("adjustment plan_id does not match tracking session")
    adjustments = [a for a in session.adjustments if a.adjustment_id != adjustment.adjustment_id]
    return session.model_copy(update={"adjustments": adjustments + [adjustment]})


def complete_plan(
    session: TrackingSession,
    after: BaselineMetrics,
    final_reflection: str,
) -> CompletionSnapshot:
    if not session.baseline:
        raise ValueError("baseline metrics are required before plan completion")
    if max((c.day for c in session.checkins), default=0) < session.duration_days:
        raise ValueError("plan cannot be completed before the final day is reached")
    return CompletionSnapshot(
        plan_id=session.plan_id,
        completed=True,
        before=session.baseline,
        after=after,
        change_awareness=round(after.awareness - session.baseline.awareness, 2),
        change_confidence=round(after.confidence - session.baseline.confidence, 2),
        change_outcome=round(after.outcome - session.baseline.outcome, 2),
        final_reflection=final_reflection,
    )
