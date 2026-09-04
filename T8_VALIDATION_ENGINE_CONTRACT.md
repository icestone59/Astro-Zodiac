# Astro-Zodiac T8 — Validation Engine Contract

Status: MVP implementation baseline

## Purpose

Validate a T6 Pattern Candidate against user-reported experience. The engine is deterministic and product-oriented.

It does **not**:
- diagnose
- claim psychometric validity
- prove astrology causes behavior
- force a pattern when the user disagrees
- use AI to score or interpret responses

## Input

```text
Pattern Candidate (T6)
+
5–8 custom MVP questions
+
User Responses (1–5)
+
Optional Behavioral Evidence
```

Question response types:
- frequency
- agreement
- behavioral example

## Output

```text
astrology_signal_score      0–30
self_report_score           0–35
behavioral_evidence_score   0–35
pattern_fit_score            0–100

fit = Low / Moderate / Strong
status = validated / explored / not_confirmed
```

Thresholds:
- 0–39 Low
- 40–69 Moderate
- 70–100 Strong

These are MVP product thresholds only.

## Scoring

### Astrology
T6 product score is normalized into 0–30 and capped.

### Self-report
5-point responses are normalized to 0–1 and mapped to 0–35. Items marked `reverse_scored` are inverted before aggregation.

### Behavioral evidence
Explicit evidence items provide a 0–1 strength. A weighted top-three aggregation maps the result to 0–35 to reduce double-counting.

## Validation behavior

At least 5 scorable responses are required before the engine can return `validated` or `not_confirmed`.

With fewer than 5 answers:
- status = `explored`
- next route = `continue_questions`

With enough answers:
- Low → `not_confirmed`
- Moderate/Strong → `validated`

A future product layer may distinguish “validated” from “explored” using more nuanced UX, but MVP must preserve the user's ability to disagree.

## Research / licensing note

The MVP questions are custom Astro-Zodiac items informed by the project's psychology reference library. They are **not** the original items of GPS-9, F-MPS, GSE, VQ, RRS, or other named instruments. The product must not call these responses a score from those instruments without separate licensing/permission and validation work.
