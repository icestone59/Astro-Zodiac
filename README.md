# T2 — Astro Calculation Engine

## What changed

`astro_calc.py` now returns the canonical `NormalizedChart` defined by T1.

### Canonical fields

Every natal point contains:

- `degree_raw`
- `sign`
- `degree_in_sign`
- `minute`
- `second`
- `dms`
- `house`
- `retrograde`
- `point_type`

House cusps contain the same degree/sign representation.

ASC/MC are represented as `ChartPoint` objects with `point_type="angle"`.

## Important migration note

This is intentionally **not** the final API migration.

The existing `main.py` still expects legacy keys such as:

- `birth_chart_degrees`
- `ruler_mapping`
- `transit_degrees`

Those will be migrated in the next stages.

Do not manually re-add those old keys into the new calculation engine.

## T2 scope

- Swiss Ephemeris natal calculation
- Tropical zodiac
- Placidus houses
- Planet house assignment
- Retrograde flag
- ASC / MC
- Chiron / Mean Node
- Uranian factors already used by the project

## Not yet implemented

- House Ruler calculation
- Natal Aspect Engine
- Uranian midpoint engine
- Pattern Engine
- Transit-to-natal engine
- Legacy API replacement


## Ephemeris path

The engine automatically uses `<project>/ephe/` when that directory exists.
This is required for Chiron and Uranian factors that depend on Swiss Ephemeris data files.

The repository's existing `ephe/` directory should remain tracked and must be deployed with the application.
