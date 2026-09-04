# Astro-Zodiac — T7 Changelog

## T7.1 — Evidence Engine Integration baseline

### Added
- `evidence_schema.py` — versioned Evidence Snapshot contract.
- `evidence_integration.py` — deterministic adapter from T6 `PatternSignal` to traceable evidence.
- `tests/test_evidence_integration.py` — baseline integration tests.

### Contract
- Evidence is generated only from structured T6 signals.
- Every evidence item retains `pattern_id`, `signal_id`, `domain`, `type`, `statement`, `source_refs`, `factors`, `weight`, and optional `orb`.
- Snapshot preserves chart schema, pattern-engine, and pattern-library versions.
- Pattern-level filtering is supported for targeted report/AI context.

### Safety / Scope
- No natural-language interpretation.
- No psychological diagnosis.
- No childhood-cause inference.
- No future-event guarantees.
- Legacy `evidence_engine.py` is intentionally not deleted or rewritten in T7.1; migration can happen after the adapter is covered by integration tests.
