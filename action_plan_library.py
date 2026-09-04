"""Astro-Zodiac T10 — deterministic action-plan templates.

Templates are deliberately finite and low-risk. They tell the engine how to
sequence a method; the user's goal statement supplies the personal context.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class StepTemplate:
    title: str
    action: str
    action_type: str
    minutes: int | None = None
    worksheet_id: str | None = None
    measurement_id: str | None = None


@dataclass(frozen=True)
class PlanTemplate:
    phase_titles: Tuple[str, ...]
    steps_by_duration: Dict[int, Tuple[StepTemplate, ...]]


BASE_MEASUREMENTS: Dict[str, Tuple[str, ...]] = {
    "P01": ("planned_actions", "completed_actions", "recovery_after_miss"),
    "P02": ("thought_clarity", "alternative_quality", "next_action_selected"),
    "P03": ("prediction_confidence", "experiment_completed", "learning_logged"),
    "P05": ("completed_actions", "confidence", "evidence_count"),
    "P06": ("value_clarity", "committed_action", "weekly_alignment"),
    "P08": ("problem_defined", "next_action", "review_completed"),
}


def _repeat_with_checkins(core: Tuple[StepTemplate, ...], duration: int, checkin_every: int = 3) -> Tuple[StepTemplate, ...]:
    steps = list(core)
    for day in range(1, duration + 1):
        if day == 1 or day % checkin_every == 0 or day == duration:
            steps.append(StepTemplate(
                title="Daily check-in",
                action="Record what you completed, what got in the way, and the next smallest step.",
                action_type="check_in",
                minutes=3,
                measurement_id="daily_progress",
            ))
    return tuple(steps)


TEMPLATES: Dict[str, PlanTemplate] = {
    "P01": PlanTemplate(
        phase_titles=("Make it concrete", "Practice starting", "Stabilize"),
        steps_by_duration={
            7: _repeat_with_checkins((
                StepTemplate("Define the trigger", "Choose one recurring moment where you delay the task.", "reflection", 5, "W01"),
                StepTemplate("Write one If-Then rule", "Write one trigger-action rule for starting within 5 minutes.", "practice", 5, "W01", "planned_actions"),
                StepTemplate("Do the smallest start", "Start the target task for one deliberately small block.", "real_world", 15, None, "completed_actions"),
                StepTemplate("Review recovery", "After any miss, restart with the smallest next step instead of extending the delay.", "practice", 5, "W02", "recovery_after_miss"),
            ), 7),
            14: _repeat_with_checkins((
                StepTemplate("Define the trigger", "Choose one recurring moment where you delay the task.", "reflection", 5, "W01"),
                StepTemplate("Write one If-Then rule", "Create one start rule and place it where you will see it.", "practice", 5, "W01", "planned_actions"),
                StepTemplate("Run small starts", "Use the rule on at least three real opportunities.", "real_world", 20, None, "completed_actions"),
                StepTemplate("Build a backup", "Create one fallback action for low-energy or disrupted days.", "practice", 5, "W02", "recovery_after_miss"),
            ), 14),
            30: _repeat_with_checkins((
                StepTemplate("Define the trigger", "Choose one recurring moment where you delay the task.", "reflection", 5, "W01"),
                StepTemplate("Write one If-Then rule", "Create one start rule and one backup rule.", "practice", 5, "W01", "planned_actions"),
                StepTemplate("Run repeated starts", "Use the rules across repeated real opportunities.", "real_world", 20, None, "completed_actions"),
                StepTemplate("Review the pattern", "Identify which triggers still produce delay and simplify the next action.", "review", 10, "W02", "recovery_after_miss"),
            ), 30),
        },
    ),
    "P02": PlanTemplate(
        phase_titles=("Notice the standard", "Test the standard", "Refine"),
        steps_by_duration={
            7: _repeat_with_checkins((
                StepTemplate("Capture one perfection loop", "Write one situation, thought, evidence and balanced alternative.", "reflection", 10, "W03", "thought_clarity"),
                StepTemplate("Run one small test", "Choose a low-stakes task and test a 'good enough' version.", "real_world", 20, "W04", "experiment_completed"),
                StepTemplate("Choose the next action", "Record one useful next step instead of waiting for certainty.", "practice", 5, "W03", "next_action_selected"),
            ), 7),
            14: _repeat_with_checkins((
                StepTemplate("Capture the standard", "Record where your internal standard creates delay or rework.", "reflection", 10, "W03", "thought_clarity"),
                StepTemplate("Run two low-stakes tests", "Test a good-enough version twice and record the observed result.", "real_world", 20, "W04", "experiment_completed"),
                StepTemplate("Refine the standard", "Write a balanced alternative that preserves quality without requiring perfection.", "practice", 10, "W03", "alternative_quality"),
            ), 14),
            30: _repeat_with_checkins((
                StepTemplate("Map the perfection loop", "Record common triggers, thoughts, evidence and next actions.", "reflection", 10, "W03", "thought_clarity"),
                StepTemplate("Run repeated experiments", "Use small behavioral tests across several low-stakes tasks.", "real_world", 20, "W04", "experiment_completed"),
                StepTemplate("Refine the standard", "Keep the quality rule that helps and remove one rule that creates unnecessary delay.", "review", 10, "W03", "alternative_quality"),
            ), 30),
        },
    ),
    "P03": PlanTemplate(
        phase_titles=("Define the decision", "Test action", "Learn"),
        steps_by_duration={
            7: _repeat_with_checkins((
                StepTemplate("Pick one reversible decision", "Choose one decision small enough to act on safely this week.", "reflection", 5, "W04"),
                StepTemplate("Run the smallest test", "Act on one option and record your prediction before acting.", "real_world", 20, "W04", "experiment_completed"),
                StepTemplate("Review learning", "Compare prediction with outcome and decide the next test.", "review", 10, "W04", "learning_logged"),
            ), 7),
            14: _repeat_with_checkins((
                StepTemplate("Pick a reversible decision", "Choose one decision with a clear next step and manageable downside.", "reflection", 5, "W04"),
                StepTemplate("Run two tests", "Make two small decisions and record predicted versus observed outcomes.", "real_world", 20, "W04", "experiment_completed"),
                StepTemplate("Automate one rule", "Create one If-Then rule for a recurring decision.", "practice", 5, "W01", "next_action"),
            ), 14),
            30: _repeat_with_checkins((
                StepTemplate("Define decision criteria", "Choose one recurring decision and write the smallest useful criteria.", "reflection", 10, "W04"),
                StepTemplate("Run repeated tests", "Make small, reversible decisions and record predictions and outcomes.", "real_world", 20, "W04", "experiment_completed"),
                StepTemplate("Review learning", "Identify what evidence helped you decide faster and more clearly.", "review", 10, "W04", "learning_logged"),
            ), 30),
        },
    ),
    "P05": PlanTemplate(
        phase_titles=("Create evidence", "Repeat mastery", "Increase challenge"),
        steps_by_duration={
            7: _repeat_with_checkins((
                StepTemplate("Choose one doable task", "Pick a task that is challenging but clearly within reach.", "reflection", 5, "W07"),
                StepTemplate("Complete and log", "Do the task and record what you actually accomplished.", "real_world", 20, "W07", "completed_actions"),
                StepTemplate("Record confidence change", "Rate confidence before and after, then note what helped.", "check_in", 5, "W07", "confidence"),
            ), 7),
            14: _repeat_with_checkins((
                StepTemplate("Choose a small mastery target", "Select one skill/task that can be practiced repeatedly.", "reflection", 5, "W07"),
                StepTemplate("Build repeated evidence", "Complete several small repetitions and log what worked.", "real_world", 20, "W07", "evidence_count"),
                StepTemplate("Increase slightly", "Raise difficulty only after the current step feels manageable.", "practice", 10, "W07", "confidence"),
            ), 14),
            30: _repeat_with_checkins((
                StepTemplate("Define a mastery ladder", "Choose a skill and three progressively harder versions of the task.", "reflection", 10, "W07"),
                StepTemplate("Build repeated evidence", "Complete repeated practice and capture specific mastery evidence.", "real_world", 20, "W07", "evidence_count"),
                StepTemplate("Increase challenge gradually", "Move to the next step only when the prior level is manageable.", "practice", 15, "W07", "confidence"),
            ), 30),
    },
    ),
    "P06": PlanTemplate(
        phase_titles=("Clarify", "Commit", "Align"),
        steps_by_duration={
            7: _repeat_with_checkins((
                StepTemplate("Choose one value", "Name one value that matters for the current goal.", "reflection", 10, "W06", "value_clarity"),
                StepTemplate("Define observable action", "Describe what living that value looks like this week.", "practice", 10, "W06", "committed_action"),
                StepTemplate("Do one aligned action", "Complete one small action that expresses the chosen value.", "real_world", 15, "W06", "committed_action"),
            ), 7),
            14: _repeat_with_checkins((
                StepTemplate("Clarify the value", "Choose one value and why it matters now.", "reflection", 10, "W06", "value_clarity"),
                StepTemplate("Create two aligned actions", "Turn the value into two concrete, controllable actions.", "practice", 10, "W06", "committed_action"),
                StepTemplate("Review alignment", "Check whether recent actions matched the value and adjust one next step.", "review", 10, "W06", "weekly_alignment"),
            ), 14),
            30: _repeat_with_checkins((
                StepTemplate("Clarify priorities", "Choose the values most relevant to the current goal.", "reflection", 10, "W06", "value_clarity"),
                StepTemplate("Build a committed-action routine", "Create repeated small actions aligned with the chosen value.", "real_world", 15, "W06", "committed_action"),
                StepTemplate("Review alignment", "Adjust actions when they drift from the selected value.", "review", 10, "W06", "weekly_alignment"),
            ), 30),
        },
    ),
    "P08": PlanTemplate(
        phase_titles=("Define", "Act", "Review"),
        steps_by_duration={
            7: _repeat_with_checkins((
                StepTemplate("Name one problem", "Write the specific problem and separate controllable from uncontrollable parts.", "reflection", 10, "W08", "problem_defined"),
                StepTemplate("Choose one next action", "Select one concrete action within your control.", "practice", 5, "W08", "next_action"),
                StepTemplate("Review result", "Record what happened and what you learned before thinking about the problem again.", "review", 10, "W08", "review_completed"),
            ), 7),
            14: _repeat_with_checkins((
                StepTemplate("Define the problem", "Separate controllable from uncontrollable parts of one recurring concern.", "reflection", 10, "W08", "problem_defined"),
                StepTemplate("Run two action cycles", "Choose a next action, do it, then review the result.", "real_world", 20, "W08", "next_action"),
                StepTemplate("Capture learning", "Write what the action changed and what still needs a decision.", "review", 10, "W08", "review_completed"),
            ), 14),
            30: _repeat_with_checkins((
                StepTemplate("Define recurring problems", "Turn repetitive thinking into specific, solvable problem statements.", "reflection", 10, "W08", "problem_defined"),
                StepTemplate("Run repeated action cycles", "Use a define → options → action → review loop on controllable problems.", "real_world", 20, "W08", "next_action"),
                StepTemplate("Review and simplify", "Keep the actions that help and remove loops that only repeat thinking.", "review", 10, "W08", "review_completed"),
            ), 30),
        },
    ),
}


def get_template(pattern_id: str, duration_days: int) -> PlanTemplate:
    try:
        template = TEMPLATES[pattern_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported MVP action-plan pattern: {pattern_id}") from exc
    if duration_days not in template.steps_by_duration:
        raise ValueError(f"Unsupported plan duration: {duration_days}")
    return template


def get_measurement_ids(pattern_id: str) -> Tuple[str, ...]:
    try:
        return BASE_MEASUREMENTS[pattern_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported MVP action-plan pattern: {pattern_id}") from exc
