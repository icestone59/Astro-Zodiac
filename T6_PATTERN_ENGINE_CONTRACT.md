# Astro-Zodiac T6 — Pattern Engine Contract

Status: T6 implementation baseline / v1

## Purpose

Combine deterministic astrology signals from T2–T5 into stable Pattern Candidates.
The Pattern Engine does **not** interpret in natural language, diagnose users, or
claim psychological causation.

## Inputs

- `NormalizedChart` from T2
- `NatalChart.house_rulers` from T3
- `NatalChart.aspects` from T4
- deterministic Uranian calculations from T5
- shared Pattern Library v1

## MVP Pattern IDs

`P01, P02, P03, P05, P06, P08`

Pattern IDs remain stable across Free, 99, and 599. The full 12-pattern library
remains defined in `pattern_library.py`, with only the six MVP patterns active in T6.

## Output

`PatternEngineResult` contains:

- `engine_version`
- `pattern_library_version`
- `ranking.primary`
- `ranking.secondary`
- `ranking.strength`
- `ranking.candidates`

Each candidate contains a stable ID, life question, validation route, score and
traceable signals.

## Scoring

The MVP score is a product prioritization score, not a psychometric confidence score:

`western + uranian + context + specificity`

Signals are strengthened when multiple independent factors converge. Tight aspects,
relevant houses/house rulers, Uranian pictures and repeated Western/Uranian themes
increase priority.

## Free Ranking

Free exposes exactly three roles when available:

1. primary blind spot
2. secondary pattern
3. strength candidate

The strength candidate uses a separate stable ID (`S01`) because the 12-pattern
problem library should not be repurposed into a positive claim.

## Boundaries

- `candidate` means "Pattern to Explore".
- No clinical diagnosis.
- No childhood-cause inference.
- No future-event guarantee.
- AI interpretation is a later layer and may only consume these structured signals.
