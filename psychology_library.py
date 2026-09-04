"""Astro-Zodiac T9 — curated self-development psychology library.

No diagnosis is inferred. Evidence sources are used as research background and
method references; original instrument items are not copied into product code.
"""
from __future__ import annotations
from typing import Dict, Tuple
from psychology_schema import EvidenceSource, InterventionMethod, WorksheetDefinition

SOURCES: Dict[str, EvidenceSource] = {
    "SRC_GPS9": EvidenceSource("SRC_GPS9", "General Procrastination Scale (GPS-9)", "A", "https://www.sciencedirect.com/science/article/pii/S0191886919302077", "Research background; do not copy items without permission."),
    "SRC_FMPS": EvidenceSource("SRC_FMPS", "Frost Multidimensional Perfectionism Scale / Brief", "A", "https://journals.sagepub.com/doi/10.1177/0734282916651359", "Research background; licensing/permission review required."),
    "SRC_DECISION": EvidenceSource("SRC_DECISION", "General Decision-Making Style / indecisiveness research", "A", "https://journals.sagepub.com/doi/10.1177/0013164495055017", "Research background; use custom product items unless licensed."),
    "SRC_GSE": EvidenceSource("SRC_GSE", "General Self-Efficacy Scale", "A", "https://eprovide.mapi-trust.org/instruments/general-self-efficacy-scale", "Source notes public-domain status; preserve original meaning/scoring if the original instrument is used."),
    "SRC_VQ": EvidenceSource("SRC_VQ", "Valuing Questionnaire", "A", "https://www.sciencedirect.com/science/article/pii/S2212144714000532", "Research background for values work."),
    "SRC_RRS": EvidenceSource("SRC_RRS", "Ruminative Responses Scale", "A", "https://doi.org/10.1023/A:1023910315561", "Research background; do not infer depression."),
    "SRC_WHO": EvidenceSource("SRC_WHO", "WHO psychological self-help guideline", "B", "https://www.who.int/publications/i/item/9789240120785", "Supports structured digital self-help with appropriate scope and safety."),
    "SRC_WOOP": EvidenceSource("SRC_WOOP", "WOOP / Mental Contrasting + Implementation Intentions", "B", "https://woopmylife.org/", "Use as structured self-development method."),
}

INTERVENTIONS: Dict[str, InterventionMethod] = {
    "I01": InterventionMethod("I01", "Implementation Intentions", "Convert intention into a concrete response to a trigger.", ("Choose one trigger (If X)", "Choose one small action (Then Y)", "Write the if-then plan", "Run it in the target situation", "Review and refine"), ("planned_actions", "completed_actions", "recovery_after_miss"), ("SRC_WOOP", "SRC_GPS9"), ("Keep the action small and reversible.", "Do not use for dangerous or clinically urgent situations.")),
    "I02": InterventionMethod("I02", "WOOP", "Clarify a desired outcome and identify the main obstacle before planning.", ("Wish", "Outcome", "Obstacle", "Plan using If X, then Y"), ("wish_clarity", "obstacle_identified", "planned_actions"), ("SRC_WOOP",), ("Keep the goal within the user's control.", "Do not frame low progress as personal failure.")),
    "I03": InterventionMethod("I03", "CBT-informed Thought Record", "Separate situation, thought, evidence and a more useful alternative.", ("Situation", "Automatic thought", "Evidence for", "Evidence against", "Balanced alternative", "Next small action"), ("thought_clarity", "alternative_quality", "next_action_selected"), ("SRC_FMPS", "SRC_RRS", "SRC_WHO"), ("Self-development only; not a clinical treatment protocol.", "Do not use for trauma processing or acute mental-health crises.")),
    "I04": InterventionMethod("I04", "Behavioral Experiment", "Test a specific prediction with a small, observable real-world action.", ("Prediction", "Small test", "Observed result", "Learning", "Next test"), ("prediction_confidence", "experiment_completed", "learning_logged"), ("SRC_FMPS", "SRC_DECISION", "SRC_WHO"), ("Only choose safe, low-stakes experiments.", "Never prescribe dangerous exposure.")),
    "I05": InterventionMethod("I05", "Graded Challenge", "Reduce avoidance by taking progressively manageable approach steps.", ("Choose safe target", "Rate difficulty 1–10", "Select easier first step", "Complete", "Increase only when manageable"), ("difficulty", "completion", "confidence_after"), ("SRC_WHO",), ("Do not use for trauma-related or dangerous exposure.", "Stop and seek appropriate professional support when a situation exceeds self-help scope.")),
    "I06": InterventionMethod("I06", "Values Clarification", "Translate important values into chosen, observable actions.", ("Name important life areas", "Choose top values", "Describe what living the value looks like", "Pick one committed action", "Review alignment"), ("value_clarity", "committed_action", "weekly_alignment"), ("SRC_VQ",), ("Values work is self-development, not diagnosis.", "Do not imply that low values alignment is a disorder.")),
    "I07": InterventionMethod("I07", "Mastery Evidence", "Build confidence from repeated evidence of capability.", ("Choose a small skill/task", "Complete it", "Record what was done", "Record what helped", "Repeat with slightly more challenge"), ("completed_actions", "confidence", "evidence_count"), ("SRC_GSE",), ("Avoid global claims such as 'you can do anything'.", "Use specific, observable mastery evidence.")),
    "I08": InterventionMethod("I08", "Problem-Solving Conversion", "Turn repetitive thinking into a concrete problem-solving loop.", ("Define the problem", "Separate controllable vs uncontrollable", "List options", "Choose one next action", "Review result"), ("problem_defined", "next_action", "review_completed"), ("SRC_RRS", "SRC_WHO"), ("Do not treat rumination as depression or another disorder.", "Escalate beyond self-help scope when appropriate.")),
}

WORKSHEETS: Dict[str, WorksheetDefinition] = {
    "W01": WorksheetDefinition("W01", "If-Then Action Plan", ("Trigger X", "Action Y", "When/Where", "Backup plan")),
    "W02": WorksheetDefinition("W02", "WOOP Sheet", ("Wish", "Outcome", "Obstacle", "If-Then Plan")),
    "W03": WorksheetDefinition("W03", "Thought Record", ("Situation", "Thought", "Evidence For", "Evidence Against", "Balanced View", "Next Action")),
    "W04": WorksheetDefinition("W04", "Behavioral Experiment", ("Prediction", "Test", "Result", "Learning", "Next Test")),
    "W05": WorksheetDefinition("W05", "Graded Challenge Ladder", ("Target", "Step", "Difficulty 1–10", "Result", "Next Step")),
    "W06": WorksheetDefinition("W06", "Values → Action", ("Value", "Why It Matters", "Observable Behavior", "Committed Action", "Review")),
    "W07": WorksheetDefinition("W07", "Mastery Evidence Log", ("Task", "What I Did", "What Helped", "Confidence Before", "Confidence After")),
    "W08": WorksheetDefinition("W08", "Think → Solve → Act", ("Problem", "Controllable?", "Options", "Next Action", "Review")),
}

PATTERN_MAP: Dict[str, Tuple[str, Tuple[str, ...], Tuple[str, ...]]] = {
    "P01": ("I01", ("I01", "I02"), ("W01", "W02")),
    "P02": ("I03", ("I03", "I04"), ("W03", "W04")),
    "P03": ("I04", ("I04", "I01"), ("W04", "W01")),
    "P05": ("I07", ("I07", "I02"), ("W07", "W02")),
    "P06": ("I06", ("I06", "I01"), ("W06", "W01")),
    "P08": ("I08", ("I08", "I03"), ("W08", "W03")),
}
