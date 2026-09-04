# Astro-Zodiac — Changelog

This file records project-level changes that affect architecture, contracts, performance, or behavior.

## 2026-09-04 — Baseline / Source of Truth Created

### Added
- `PROJECT_SPEC.md`
- `ARCHITECTURE.md`
- `DATA_CONTRACT.md`
- `CHANGELOG.md`
- `AI_CODING_RULES.md`

### Baseline observations from current `main` branch
- `main.py` imports the expected cache functions and AI functions, but callers and implementations must be checked as a single dependency set.
- Current `astro_calc.py` exposes a calculation shape centered on `user_info`, `planets`, `angles`, and `houses`; other modules expect a different shape (`birth_chart_degrees`, `ruler_mapping`, etc.).
- Current `evidence_engine.py` expects fields such as `degree_raw`, `house`, and `ruler_mapping`.
- Current `ai_service.py` contains a monolithic `analyze_ai_service()` flow and calculates realtime transits during AI calls.
- Current prompt rules enforce strict evidence grounding and multi-paragraph category output.
- Current frontend exposes package levels `pkg1` through `pkg4` and controls question/deep-report UI based on package selection.

### Decision
The next implementation work must first establish the canonical chart schema and deterministic calculation/evidence contracts before broad refactoring of the frontend or AI prompts.

## Change Entry Template
```text
## YYYY-MM-DD — <title>

### Changed
- file/module:
- what changed:

### Why
- reason:

### Contract Impact
- none / describe exact change

### Tests
- command:
- result:

### Performance
- before:
- after:

### Migration / Rollback
- notes:
```
