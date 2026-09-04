# Astro-Zodiac — Architecture

## 1. Canonical Flow
```text
[Frontend]
    |
    v
[API / Orchestrator]
    |
    +--> [Chart Cache]
    |
    v
[Astrology Calculation Engine]
    |
    v
[Normalized Chart Schema]
    |
    +--> [House Ruler Engine]
    +--> [Natal Aspect Engine]
    +--> [Transit Engine]
              |
              v
        [Evidence Engine]
              |
              v
        [Pattern Engine]
              |
              v
       [Validation Engine]
              |
              v
     [Intervention Engine]
              |
              v
       [Life Plan Engine]
              |
              v
        [AI Personalization]
              |
              v
        [Tracking / Progress]
              |
              v
          [Report JSON]
              |
              v
          [Frontend]
```


## 1A. Product / Transformation Architecture
```text
FREE DISCOVERY
    ↓
PATTERN TO EXPLORE
    ↓
VALIDATION
    ↓
INTERVENTION SELECTION
    ↓
ACTION PLAN
    ↓
WORKSHEET
    ↓
TRACKING
    ↓
PROGRESS
```

Package responsibilities:
- Free: discovery and Aha Moment.
- 99: validation of relevant patterns.
- 599: personalized action plan.
- 1,999: structured transformation and tracking.

## 1B. Performance / UX Rule
Free must feel immediate. Avoid blocking the user on a monolithic report. Use progressive results, targeted evidence, streaming where useful, and cache deterministic work.

## 2. Module Responsibilities

### `main.py`
Owns HTTP routes and orchestration only.
- Validate request input.
- Call calculation/evidence/report services.
- Handle errors.
- Must not contain astrology formulas.
- Must not duplicate prompt/business rules.

### `astro_calc.py`
Owns deterministic astronomical calculation.
- Birth chart positions.
- Angles.
- House cusps.
- Transit positions.
- Time/location conversion.

It must emit the canonical chart schema or call a dedicated normalizer.

### `chart_schema.py` (planned)
Owns the canonical data contract.
- Typed models/dicts.
- Stable field names.
- Schema version.
- Serialization rules.

No module should invent a second chart shape.

### `house_ruler.py` (planned)
Owns:
- House cusp sign.
- Sign ruler.
- Ruler planet placement.
- House ruler metadata.

### `aspect_engine.py` (planned)
Owns natal/transit aspect calculations.
- Supported aspects.
- Orb rules.
- Exact angular difference.
- Optional applying/separating logic where mathematically available.

### `pattern_engine.py` (planned)
Owns conversion of deterministic astrology evidence into exploratory life-pattern hypotheses. It must not make clinical diagnoses.

### `validation_engine.py` (planned)
Owns self-assessment, behavioral evidence, confidence scoring, and validation state.

### `intervention_engine.py` (planned)
Owns selection and execution of structured interventions from the Psychology / Intervention Library.

### `life_plan_engine.py` (planned)
Owns action plans, milestones, worksheets, and next actions.

### `tracking_engine.py` (planned)
Owns action completion, check-ins, weekly reviews, progress scoring, and plan adjustments.

### `evidence_engine.py`
Owns selection and organization of deterministic facts for each analysis category.
It may compute evidence from already-normalized data, but it must not use an LLM.

### `ai_service.py`
Owns provider calls and interpretation.
- Receives targeted evidence.
- Receives prompt/schema versions.
- Returns structured report data.
- Must not calculate astrology.

### `prompts.py`
Owns interpretation instructions only.
Prompts must consume evidence, not raw ambiguous chart structures.

### `database.py`
Owns persistence/cache only.
- Chart cache.
- AI report cache.
- Cache keys.
- Schema initialization/migrations.

### `logic.js`
Owns frontend state and rendering only.
- Collect input.
- Call API.
- Render API response.
- Manage package/UI state.

No astrology calculation logic belongs here.

### `index.html` / `deepreport.html`
Presentation layer only.

### `ephe/`
Swiss Ephemeris files. Treat as external calculation data; do not modify without a specific technical reason.

## 3. Dependency Rules
Allowed:
```text
main → calc/evidence/AI/database
AI → prompts
Evidence → chart schema / calculation outputs
Frontend → API
```

Not allowed:
```text
Frontend → astrology formulas
AI service → astrology calculations
Prompt → database internals
Database → frontend
Calculation engine → UI
```

## 4. Request Pipelines

### Natal Report
```text
POST /calculate_chart
→ normalized chart
→ evidence matrix
→ AI natal analysis
→ cached report
```

### Transit Q&A
```text
existing normalized natal chart
+ transit calculation for requested date/time
+ relevant evidence
→ AI answer
→ question-specific cache
```

### Deep Report
```text
normalized natal chart
+ deep evidence
+ optional midpoint/Uranian evidence
→ structured AI report
→ radar/bar metrics
→ cache
```

## 5. Performance Architecture
Do not do this:
```text
AI request
→ calculate whole natal chart
→ calculate all transits
→ send whole chart
→ generate huge report
```

Prefer:
```text
calculate once
→ normalize once
→ cache
→ select only relevant evidence
→ send compact prompt
→ stream/progress UI where useful
```

## 6. Versioning
Any change to the canonical schema, prompt contract, calculation rules, or cache-key strategy requires:
1. version increment;
2. changelog entry;
3. affected tests updated;
4. compatibility decision documented.
