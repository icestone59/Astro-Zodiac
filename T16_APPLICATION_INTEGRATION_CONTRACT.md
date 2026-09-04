# ASTRO-ZODIAC T16 — API / APPLICATION INTEGRATION CONTRACT v1

Goal: one thin orchestration layer that composes T2–T15 without moving domain logic into `main.py`.

Pipeline:
`HTTP Adapter -> Auth/Membership -> T16 -> T2 Chart -> T3 House Ruler -> T4 Aspect -> T5 Uranian -> T6 Pattern -> T7 Evidence -> T8 Validation -> T9 Psychology -> T10 Action Plan -> T11 Tracking`

Boundaries:
- T13 owns identity/session semantics.
- T12/T15 own entitlement and payment-to-access.
- T2–T11 own deterministic domain calculations.
- T16 only orchestrates and shapes application responses.
- No payment SDK, PostgreSQL, AI generation, or frontend code is added here.

Fast path: `BirthChartRequest -> analyze_free()`; chart is calculated/enriched once and then reused downstream.

Guards: Psychology and Action Plan require a validated pattern. Entitlement remains server-side.
