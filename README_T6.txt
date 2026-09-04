ASTRO-ZODIAC T6 — PATTERN ENGINE

Copy these files into the repository root (same level as chart_schema.py / uranian_engine.py):
- pattern_schema.py
- pattern_library.py
- pattern_engine.py
- T6_PATTERN_ENGINE_CONTRACT.md
- CHANGELOG_T6.md
- tests/test_pattern_engine.py

Then run:
  python -m pytest -q tests/test_pattern_engine.py

Do not modify main.py integration yet. T6 is the deterministic Pattern layer only.
