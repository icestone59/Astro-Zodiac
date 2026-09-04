# T5 — Uranian Engine

## Scope

T5 adds technical Uranian calculations only:

- 90° dial normalization
- 90° axis distance
- midpoint longitude
- midpoint axis
- planetary picture detection A/B=C

## Important

This engine does **not** decide what a picture means psychologically or predictively.

It returns structured evidence for later layers.

## 90° Dial

The engine folds ecliptic longitudes into 0..90 so conjunction/square/opposition relationships can be compared on the same dial.

## Midpoint Rule

MVP uses the midpoint on the shortest arc and then folds it to the 90° axis.

For diametrically opposite points there are equivalent midpoint directions; the engine stores one canonical result and the 90° axis is what the Evidence layer should use.

## Planetary Pictures

MVP supports the basic relation:

A/B=C

with configurable orb.

## T5 does not yet include

- TNP interpretation
- hypothetical planet semantics
- midpoint trees/UI
- user-specific orb presets
- advanced 45° dial
- transit-to-natal Uranian activation
- psychological interpretation
