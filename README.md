# T4 — Natal Aspect Engine

## Scope

T4 adds deterministic major natal aspects from the canonical T1/T2 schema:

- Conjunction 0°
- Sextile 60°
- Square 90°
- Trine 120°
- Opposition 180°

The engine returns the canonical `Aspect` model.

## Orb

MVP uses point-based default orbs and takes the larger orb of the two participating points.

Current defaults are intentionally explicit and can be replaced later by versioned user settings.

## Applying / Separating

T4 leaves `applying = None`.

A reliable implementation should be added only after:
- consistent planetary speed is stored in the schema,
- a policy for Nodes/Chiron/angles is defined,
- applying/separating rules are versioned.

## Uranian

Uranian hypothetical factors are excluded from the standard natal major-aspect set by default. A dedicated Uranian engine will handle 90° structures and midpoints in a later stage.

## Important

T4 calculates aspects only.
It does not interpret the aspect psychologically or astrologically.
