# Astro-Zodiac T9 — Psychology Engine Contract v1

## Purpose
Convert a **validated** Astro-Zodiac Pattern into a deterministic self-development recommendation.

## Input
- `pattern_id`
- `validation_status`
- `pattern_fit_score`

## Gate
Only `validation_status == validated` may receive an intervention recommendation.
`explored` and `not_confirmed` stop before intervention selection.

## Output
- primary intervention
- alternative intervention(s)
- worksheet(s)
- measurement indicators
- evidence source IDs
- safety rules
- rationale

## MVP mappings
| Pattern | Primary | Alternatives |
|---|---|---|
| P01 | I01 Implementation Intentions | I02 WOOP |
| P02 | I03 CBT-informed Thought Record | I04 Behavioral Experiment |
| P03 | I04 Behavioral Experiment | I01 Implementation Intentions |
| P05 | I07 Mastery Evidence | I02 WOOP |
| P06 | I06 Values Clarification | I01 Implementation Intentions |
| P08 | I08 Problem-Solving Conversion | I03 CBT-informed Thought Record |

## Safety
- Self-development only; not diagnosis or treatment.
- Astrology is not used as evidence of a clinical condition.
- Do not prescribe dangerous exposure, trauma processing, or other interventions beyond self-help scope.
- Preserve source/license metadata; research evidence does not automatically grant commercial reuse rights.

## Boundary
T9 recommends the **method**. It does not generate a personalized long-term action plan yet. That belongs to T10 — Action Plan Engine.
