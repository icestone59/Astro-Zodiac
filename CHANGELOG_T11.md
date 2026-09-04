# CHANGELOG — T11 Tracking Engine

## T11.1

Added deterministic tracking layer for the 599 Personal Action Plan journey.

### Added
- `tracking_schema.py`
- `tracking_engine.py`
- `T11_TRACKING_ENGINE_CONTRACT.md`

### Capabilities
- Tracking session lifecycle for T10 plans
- Daily check-in validation
- Progress indicators: awareness / behavior / consistency / outcome
- Weekly review schema and handoff
- 3-failure adaptation recommendation
- Before/after completion snapshot
- Stable plan reference derived from T10 plan fields

### Product Boundary
Tracking indicators are self-development/product metrics, not clinical or psychometric scores.
