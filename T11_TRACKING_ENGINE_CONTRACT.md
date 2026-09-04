# Astro-Zodiac T11 — Tracking Engine Contract v1

## Purpose
Track a T10 Action Plan with observable self-development indicators and a non-judgmental adaptation loop.

## Input
- T10 `ActionPlan`
- Optional baseline metrics: awareness, confidence, outcome (1–10)
- Daily check-ins
- Weekly reviews

## Output
- Tracking session
- Progress metrics
- Weekly review records
- Adaptation recommendation after repeated non-completion
- Completion snapshot: before / after / change

## Daily Check-in
Required:
- status: `completed | partial | not_completed`
- difficulty: 1–10
- confidence: 1–10

Optional:
- reflection
- outcome: 1–10

When `not_completed`, `failure_reason` is required.

## Progress Logic
Progress is a composite product indicator:

```text
Awareness + Behavior + Consistency + Self-rated Outcome
```

It is **not** a clinical score, diagnosis, or psychometric validity metric.

## Failed Action Handling
After 3 consecutive failed check-ins, the engine proposes one adjustment route:
- make it smaller
- change timing
- change environment
- change trigger
- change worksheet

The purpose is adaptation, not punishment.

## Weekly Review
The schema captures:
1. What worked well?
2. What got in the way?
3. When did the Pattern show up?
4. Which intervention helped?
5. What will change next period?

## Completion
A plan can produce a completion snapshot after the final day is reached and a baseline exists. Compare before/after self-ratings and capture a final reflection.

## Boundary
T11 does not diagnose, treat, infer disorders, or claim behavior change proves an astrological cause.
