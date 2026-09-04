"""Astro-Zodiac T10 — deterministic Life Action Plan Engine."""
from __future__ import annotations

from typing import Iterable, List

from action_plan_library import get_measurement_ids, get_template
from action_plan_schema import ActionPhase, ActionPlan, ActionStep, GoalContext, ProgressCheck
from psychology_schema import PsychologyEngineResult

SUPPORTED = frozenset(("P01", "P02", "P03", "P05", "P06", "P08"))


def _split_into_phases(days: int, phase_count: int) -> List[range]:
    phase_count = min(phase_count, days)
    ranges: List[range] = []
    base = days // phase_count
    remainder = days % phase_count
    start = 1
    for idx in range(phase_count):
        length = base + (1 if idx < remainder else 0)
        stop = start + length
        ranges.append(range(start, stop))
        start = stop
    return ranges


def build_action_plan(
    psychology_result: PsychologyEngineResult,
    goal: GoalContext,
) -> ActionPlan:
    rec = psychology_result.recommendation
    pattern_id = rec.pattern_id
    if pattern_id not in SUPPORTED:
        raise ValueError(f"Unsupported MVP action-plan pattern: {pattern_id}")
    context_status = "validated"
    if context_status != "validated":  # explicit boundary for future schema extension
        raise ValueError("Action plans require a validated pattern")

    duration = goal.preferred_duration_days
    template = get_template(pattern_id, duration)
    raw_steps = template.steps_by_duration[duration]

    phases = []
    phase_ranges = _split_into_phases(duration, len(template.phase_titles))
    for index, (phase_title, day_range) in enumerate(zip(template.phase_titles, phase_ranges), start=1):
        phase_days = list(day_range)
        if not phase_days:
            continue
        phase_steps: List[ActionStep] = []
        for step_index, step_template in enumerate(raw_steps, start=1):
            # Deterministically spread core steps across phase ranges and keep check-ins recurring.
            if step_template.action_type == "check_in":
                # daily check-ins are instantiated separately below
                continue
            assigned_day = phase_days[min(index - 1, len(phase_days) - 1)]
            phase_steps.append(ActionStep(
                step_id=f"T10-{pattern_id}-P{index:02d}-S{step_index:02d}",
                day=assigned_day,
                title=step_template.title,
                action=step_template.action,
                action_type=step_template.action_type,  # type: ignore[arg-type]
                duration_minutes=step_template.minutes,
                worksheet_id=step_template.worksheet_id,
                measurement_id=step_template.measurement_id,
            ))
        phases.append(ActionPhase(
            phase_id=f"T10-{pattern_id}-P{index:02d}",
            title=phase_title,
            purpose=(
                "Turn the validated pattern into small, observable actions while preserving user control "
                "over the goal and pace."
            ),
            days=phase_days,
            steps=phase_steps or [ActionStep(
                step_id=f"T10-{pattern_id}-P{index:02d}-S01",
                day=phase_days[0],
                title="Work the method",
                action="Complete the smallest safe action from the selected intervention.",
                action_type="practice",
                duration_minutes=10,
                worksheet_id=rec.worksheet_ids[0] if rec.worksheet_ids else None,
            )],
        ))

    # Add deterministic daily check-ins to the final phase so tracking has a clear handoff.
    final_phase = phases[-1]
    existing_ids = {s.step_id for phase in phases for s in phase.steps}
    for day in range(1, duration + 1):
        if day == 1 or day % 3 == 0 or day == duration:
            sid = f"T10-{pattern_id}-CHECK-{day:02d}"
            if sid in existing_ids:
                continue
            final_phase.steps.append(ActionStep(
                step_id=sid,
                day=day,
                title="Daily check-in",
                action="Record what you completed, what got in the way, and the next smallest step.",
                action_type="check_in",
                duration_minutes=3,
                measurement_id="daily_progress",
            ))

    checks = [
        ProgressCheck(check_id="T10-PROGRESS-START", day=1, prompt="What did you commit to start, and what is the smallest next action?", metric_ids=["daily_progress"]),
        ProgressCheck(check_id="T10-PROGRESS-MID", day=max(2, duration // 2), prompt="What is working, what is getting in the way, and what should be simplified?", metric_ids=["daily_progress"]),
        ProgressCheck(check_id="T10-PROGRESS-END", day=duration, prompt="What changed, what evidence did you collect, and what should happen next?", metric_ids=["daily_progress", "plan_review"]),
    ]

    measurements = list(get_measurement_ids(pattern_id))
    if "daily_progress" not in measurements:
        measurements.append("daily_progress")
    measurements.append("plan_review")

    safety = list(dict.fromkeys(rec.safety_rules + (
        "This action plan is for self-development, not diagnosis or treatment.",
        "Keep actions safe, reversible, and within your control.",
        "Do not use the plan for acute mental-health crises, dangerous exposure, or trauma processing.",
    )))

    return ActionPlan(
        pattern_id=pattern_id,
        primary_intervention_id=rec.primary_intervention_id,
        worksheet_ids=list(rec.worksheet_ids),
        duration_days=duration,
        goal=goal,
        phases=phases,
        progress_checks=checks,
        measurement_ids=measurements,
        safety_rules=safety,
    )
