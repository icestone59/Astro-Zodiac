# Astro-Zodiac T10 — Action Plan Engine Contract v1

## Purpose
Convert a **validated** Pattern plus the T9 Psychology Recommendation into a finite, observable action plan.

## Input
- `PsychologyEngineResult` from T9
- `GoalContext`
  - user-provided goal statement
  - optional reason
  - duration: 7 / 14 / 30 days

## Gate
Only the T9 recommendation for a validated pattern is accepted.

## Output
- fixed-duration ActionPlan
- goal carried through unchanged
- phased actions
- worksheet references
- measurement IDs
- progress checks
- safety rules
- tracking handoff

## MVP Pattern Support
P01, P02, P03, P05, P06, P08

## Product Boundary
T10 does **not** use AI to invent a goal or claim a plan is clinically personalized. The user owns the goal; the engine selects and sequences a deterministic plan template tied to the validated Pattern + T9 intervention.

## UX Handoff
```text
99 Validation
    ↓
599 Goal
    ↓
T9 Intervention
    ↓
T10 Action Plan
    ↓
Worksheet / Daily Check-in
    ↓
T11 Tracking (future)
```

## Safety
- Self-development only; not diagnosis or treatment.
- Keep actions safe, reversible, and within the user's control.
- No dangerous exposure or trauma processing.
- Preserve evidence/source metadata inherited from T9.
