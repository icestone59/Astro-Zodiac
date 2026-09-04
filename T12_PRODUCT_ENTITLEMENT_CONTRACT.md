# Astro-Zodiac T12 — Product & Entitlement Engine Contract v1

## Purpose
Provide one deterministic, data-driven entitlement layer for Free / 99 / 599 / 1,999 without hard-coding package rules into routes or UI.

## Product lines
- `free` — Discovery
- `personal_insight_99` — Personal Insight
- `action_plan_599` — Personal Action Plan
- `astro_professional_1999` — Astro Professional (separate product line)

## Locked MVP entitlements
- Free: Top 3 discovery patterns.
- 99: full evidence + validation + 3 AI Personal Insight questions.
- 599: 99 + psychology intervention + action plan + tracking + 10 AI Life Planning questions.
- 1,999: professional astrology workspace features including natal, house ruler, aspects, Uranian, transit, evidence matrix, deep report, client history, export.
- Professional AI quota is intentionally **not locked** in T12.

## Rules
1. UI must ask the entitlement engine; it must not implement product checks itself.
2. Backend remains authoritative; this layer does not trust client-supplied product flags.
3. AI quota counts one successful user question. API errors/timeouts are handled by the AI service and must not consume quota.
4. Payment, authentication, persistence, refunds, and webhooks are outside T12.
5. Product access is not psychometric validity and does not imply that astrology is scientifically validated.

## Handoff
```text
T6 Pattern → T7 Evidence → T8 Validation → T9 Psychology → T10 Action Plan → T11 Tracking
                                            ↓
                                      T12 Entitlement
                                            ↓
                                   API / Auth / Billing
```
