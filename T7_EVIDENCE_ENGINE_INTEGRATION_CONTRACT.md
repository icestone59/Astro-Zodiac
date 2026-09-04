# Astro-Zodiac T7 — Evidence Engine Integration Contract

Status: T7.1 implementation baseline

## Purpose

Create the deterministic evidence layer between T6 Pattern Engine and later
Validation / Report / AI consumers.

## Input

```text
NormalizedChart
+
PatternEngineResult
+
PatternCandidate.signals
```

## Output

```text
EvidenceSnapshot
  └── PatternEvidence[]
        └── EvidenceItem[]
```

## Evidence Item

Each evidence item preserves:

- `pattern_id`
- `signal_id`
- `domain`
- `type`
- `statement`
- `source_refs`
- `factors`
- `weight`
- `orb`

`statement` is the deterministic fact text already produced from structured
astrology signals. The adapter must not add interpretive claims.

## Versioning

The snapshot records:

- chart schema version
- source Pattern Engine version
- Pattern Library version
- Evidence Engine version

This supports reproducibility and future report evidence snapshots.

## Migration Rule

The existing legacy `evidence_engine.py` remains untouched in this step.
The adapter-first approach follows the repository migration principle:

```text
Legacy
  ↓
Adapter
  ↓
New Contract
  ↓
Tests
  ↓
Switch Traffic
  ↓
Remove Legacy
```

## Boundaries

T7.1 does not perform user validation, psychology scoring, AI interpretation,
or report generation.
