# Astro-Zodiac — AI Coding Rules

These rules apply to any AI (ChatGPT, Gemini, Claude, Copilot, etc.) working on this repository.

## 1. Before Editing
1. Read `PROJECT_SPEC.md`.
2. Read `ARCHITECTURE.md`.
3. Read `DATA_CONTRACT.md`.
4. Read the latest `CHANGELOG.md` entries.
5. Inspect the current repository files that will be affected.
6. Trace imports/callers before changing a function signature.

## 2. Source of Truth
The repository is the source of truth for code.
These markdown files are the source of truth for architecture and contracts.
Do not rely on memory of an earlier chat session.

## 3. Safe Editing Rules
- Do not rewrite an entire file when a focused change is sufficient.
- Do not create duplicate functions with the same responsibility.
- Do not silently rename fields used by other modules.
- Do not invent missing functions just to make an import pass.
- Do not change astrology rules without documenting the rule and adding/updating tests.
- Do not modify frontend code to hide a backend contract error.
- Do not remove working logic without identifying what replaces it.
- Do not introduce a second chart schema.

## 4. Astrology Rules
- Astronomy/astrology calculations are deterministic code.
- LLMs interpret; they do not calculate.
- House, sign, degree, ruler and aspect facts must come from structured calculation/evidence.
- The AI must never be allowed to "correct" a chart by intuition.

## 5. Performance Rules
- Avoid unnecessary repeated Swiss Ephemeris calls.
- Cache deterministic chart calculations.
- Do not calculate realtime transits during a natal-only AI request.
- Do not send the whole chart to the LLM when a targeted evidence payload is enough.
- Prefer smaller prompts and structured output.
- Track latency by stage when debugging slowness.

## 6. Testing Rules
Every logic change must have a relevant test or an explicit reason why a test is not practical.

Minimum checks before declaring a backend change done:
```bash
python -m compileall .
```

Then run the project's unit/integration tests when available.

For astrology calculation changes, run golden-chart tests and compare:
- planet longitudes;
- ASC/MC;
- house cusps;
- house placements;
- rulers;
- aspects.

## 7. Change Protocol
For every code change, report:
```text
Files changed:
Reason:
Contract impact:
Tests run:
Performance impact:
Known limitations:
```

Then update `CHANGELOG.md`.

## 8. If an Error Appears
Do not immediately patch the failing line.

First determine:
1. Is this a syntax/import error?
2. Is this a schema mismatch?
3. Is this a caller/callee mismatch?
4. Is this a calculation bug?
5. Is this an external dependency/configuration issue?
6. Is the error caused by stale cache data?

Fix the root cause at the correct layer.

## 9. No Guessing
If the current repository differs from these documents, inspect the current code first and update the documents only when the new behavior is intentionally adopted.

Never claim a test passed if it was not actually run.
