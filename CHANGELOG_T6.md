# T6 — Pattern Engine

## Added

- `pattern_schema.py` — stable Pattern Candidate / Score / Signal contracts.
- `pattern_library.py` — one shared Pattern Library v1 with all 12 IDs and six MVP-active patterns.
- `pattern_engine.py` — deterministic integration of T2/T3/T4/T5 into Pattern Candidates and Free Top-3 ranking.
- `T6_PATTERN_ENGINE_CONTRACT.md` — module contract and scoring/ranking rules.
- `tests/test_pattern_engine.py` — baseline contract tests.

## Design Notes

- Pattern scoring is prioritization only, not psychological measurement.
- Pattern IDs stay stable across products.
- Strength is represented separately as `S01 Agency / Capability Potential` rather than reusing a problem-pattern ID.
- No AI interpretation is included in T6.
