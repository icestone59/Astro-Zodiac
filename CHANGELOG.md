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

## 2026-09-04 — Product Direction Locked

### Changed
- Locked the commercial product ladder:
  - FREE = Discovery
  - 99 THB = Validation
  - 599 THB = Action
  - 1,999 THB = Transformation
- Added the product-to-action loop: Astrology/Uranian → Pattern → Validation → Psychology/Intervention → Action Plan → Worksheet → Tracking → Progress.
- Added `PRODUCT_BLUEPRINT.md` as the detailed commercial/product source of truth.
- Added planned Pattern, Validation, Intervention, Life Plan, Worksheet, Tracking, and Progress layers.
- Defined 80%+ Free-to-Paid upgrade as a north-star optimization target, not an assumed fact.
- Added product safety boundaries against clinical diagnosis claims from astrology.

### Contract Impact
- Product/package contracts are now part of the intended architecture.
- Server-side package enforcement and conversion event tracking are required.

### Implementation Status
- No production code was changed in this step.
- This entry records product direction before Phase 1 implementation.

## 2026-09-04 — Product/UX v4 Baseline

- Locked one shared Pattern Library across Free, 99 and 599.
- Free exposes Top 3: Blind Spot, Secondary Pattern, Strength.
- 99 validates selected Pattern(s) from Free.
- 599 uses validated Pattern(s) and Pattern Clusters for intervention/action planning.
- Pattern IDs remain stable across packages.
- No package-specific Pattern Engine or duplicate Pattern Library.
