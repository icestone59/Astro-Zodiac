# Astro-Zodiac — Project Specification

## 1. Product Objective
Astro-Zodiac is an astrology analysis product, not a generic chatbot that guesses or invents astrology.

Core promise:
- Calculate astrology deterministically.
- Build explicit astrological evidence.
- Use AI only to interpret that evidence and present it clearly.
- Deliver useful self-understanding, life-pattern insight, and timing guidance.

The product should feel fast. Calculation must be near-instant; AI generation should be optimized and progressive rather than forcing the user to wait for a large monolithic report.

## 2. Product Direction
Primary positioning:
> AI Astrology Analysis — understand your life patterns from your birth chart.

Do not position the core product as "AI predicts your future".

Planned product ladder:
1. Astro Profile — accessible entry product; personality, strengths, career, money, relationships, potential.
2. Life Strategy — deeper practical analysis for career, money, business, relationships, blind spots and decision patterns.
3. Deep Analysis — premium pattern analysis using natal, house ruler, aspects, midpoint/Uranian logic, and transit timing.

These product labels are directional. Pricing and final commercial packaging may change without changing the calculation/evidence architecture.

## 3. Non-Negotiable Principles
1. Astrology facts come from the calculation engine, not from the LLM.
2. The LLM must not invent planet positions, signs, houses, rulers, aspects, dates, or orbs.
3. Every substantive interpretation must be traceable to an evidence item.
4. A single canonical chart schema is the source of truth between modules.
5. No duplicate business logic in frontend and backend.
6. Prefer small, testable modules over repeated rewrites of whole files.
7. Never fix one error by silently changing an unrelated contract.
8. Performance is a product requirement, not an afterthought.

## 4. Target Architecture
User Input
→ Astrology Calculation Engine
→ Normalized Chart
→ House Ruler Engine
→ Natal Aspect Engine
→ Transit Engine
→ Evidence Engine
→ AI Interpretation
→ Report JSON
→ Frontend

## 5. Technology Direction
- Python backend
- Swiss Ephemeris for astronomical calculations
- Flask/API layer unless deliberately migrated with a documented decision
- SQLite/cache may remain for local/simple deployment; schema must be documented
- Browser frontend should consume API responses and render them; it must not recalculate astrology

## 6. Performance Requirements
- Do not call real-time transit calculation during every AI request when the data is not required.
- Do not send the entire chart plus unrelated data to the LLM for every category/question.
- Cache deterministic chart calculations.
- Cache AI results using stable keys that include chart identity, report type, prompt/schema version, and question when relevant.
- Prefer targeted evidence payloads per report/category.
- Prefer progressive UI updates for long reports.
- Measure latency for calculation, evidence building, AI call, and total response separately.

Initial targets:
- Cached chart calculation: < 100 ms server-side target.
- Evidence generation: < 100 ms target for normal natal chart.
- AI first visible result: aim for a few seconds, not tens of seconds, after provider/network conditions are accounted for.
- Full premium report may take longer, but UI must communicate progress and should not look frozen.

## 7. Product Modules
### Natal 7 Categories
- personality
- finance
- career
- love
- shadow_wound
- potential_growth
- additional seventh category must be explicitly named in the schema/prompt; never silently rely on inconsistent labels

### Transit Q&A
Question-driven analysis. Only relevant natal and transit evidence should be sent to AI.

### Deep Report
Premium analysis. May include deeper patterns and Uranian/midpoint logic after those engines are deterministic and tested.

## 8. Current Repository Reality
The current public repository contains the main modules: `main.py`, `astro_calc.py`, `evidence_engine.py`, `ai_service.py`, `prompts.py`, `database.py`, `index.html`, `deepreport.html`, `logic.js`, `quotes.js`, `init_db.py`, `requirements.txt`, and `ephe/`.

The repository currently contains integration mismatches that must be treated as known baseline defects, not patched blindly.

Examples observed in the current main branch:
- `main.py` expects `calculate_chart()` to return `birth_chart_degrees` and `ruler_mapping`, while the current `calculate_natal_chart()` returns `user_info`, `planets`, `angles`, and `houses`.
- `evidence_engine.py` expects `degree_raw`, `house`, and ruler mappings that the current calculation output does not consistently provide.
- The current AI service is centered on `analyze_ai_service()`, while `main.py` imports `analyze_natal_7_categories`, `analyze_transit_qa`, and `analyze_deep_report`.
- The current database layer now includes chart-cache getters/setters, but all callers must be verified against its exact schema/keys before further changes.
- The current AI service calculates fresh real-time transits inside an AI request, which should be decoupled and only used when required.

These are baseline observations for this version of the repository and must be re-verified from the repository before changing code.

## 9. Definition of Done
A feature is not done when it merely stops one error.

Done means:
- Contract is documented.
- Code compiles/imports.
- Relevant tests pass.
- Existing golden chart results are unchanged unless the change is intentional.
- API request/response shape is documented.
- Cache behavior is verified.
- Performance impact is understood.
- CHANGELOG is updated.
