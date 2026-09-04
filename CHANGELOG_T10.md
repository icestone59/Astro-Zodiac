# CHANGELOG — T10

## T10.1 — Action Plan Engine

### Added
- `action_plan_schema.py`
- `action_plan_library.py`
- `action_plan_engine.py`
- `tests/test_action_plan_engine.py`
- `T10_ACTION_PLAN_ENGINE_CONTRACT.md`
- `README_T10.txt`

### Behavior
- Converts T9 validated psychology recommendation into 7/14/30-day deterministic plan.
- Preserves user goal statement.
- Adds phases, actions, worksheets, measurements, progress checks, and safety rules.
- Supports MVP patterns P01/P02/P03/P05/P06/P08.

### Boundary
- No AI-generated plan content.
- No clinical diagnosis/treatment claims.
- Tracking remains the next milestone.
