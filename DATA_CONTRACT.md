# Astro-Zodiac — Data Contract

## 1. Rule
There must be one canonical representation of a chart between calculation, evidence, AI, and frontend layers.

Do not introduce aliases such as `deg_dec`, `degree_raw`, and `degree_total` with different meanings without documenting the distinction.

## 2. Canonical Chart Shape (Target)
```json
{
  "schema_version": "1.0",
  "user_info": {
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "timezone": "Asia/Bangkok",
    "location_name": "Bangkok",
    "latitude": 13.7563,
    "longitude": 100.5018
  },
  "angles": {
    "ASC": {
      "longitude": 12.3456,
      "sign": "Aries",
      "degree_in_sign": 12.3456,
      "dms": "12°20'44\""
    },
    "MC": {
      "longitude": 123.4567,
      "sign": "Leo",
      "degree_in_sign": 3.4567,
      "dms": "3°27'24\""
    }
  },
  "houses": {
    "House_1": {"cusp_longitude": 12.3456, "sign": "Aries"}
  },
  "planets": {
    "Sun": {
      "longitude": 63.8167,
      "sign": "Gemini",
      "degree_in_sign": 3.8167,
      "house": 10,
      "retrograde": false,
      "dms": "3°49'00\""
    }
  },
  "house_rulers": {
    "House_1": {
      "cusp_sign": "Aries",
      "ruler_planet": "Mars",
      "ruler_house": 9,
      "ruler_sign": "Aries",
      "ruler_longitude": 81.0167
    }
  }
}
```

This is the target contract. Existing code may not yet conform.

## 3. Field Semantics
- `longitude`: absolute zodiac longitude, 0–360.
- `sign`: one of the 12 canonical English sign IDs.
- `degree_in_sign`: 0–<30.
- `dms`: display-only representation.
- `house`: integer 1–12.
- `retrograde`: boolean when applicable.
- `cusp_longitude`: absolute longitude of the house cusp.
- `ruler_planet`: deterministic ruler selected by the configured rulership system.

Never infer `house` from the display string after the fact. The calculation/house engine must provide it.

## 4. Aspect Contract (Target)
```json
{
  "p1": "Sun",
  "p2": "Saturn",
  "aspect": "opposition",
  "exact_angle": 180.0,
  "actual_difference": 178.6,
  "orb": 1.4,
  "symbol": "☍"
}
```

## 5. Evidence Contract (Target)
```json
{
  "schema_version": "1.0",
  "category": "career",
  "evidence": [
    {
      "type": "house_ruler",
      "house": 10,
      "statement": "House 10 cusp is Capricorn; ruler Saturn is in House 12.",
      "source_refs": ["House_10", "Saturn"]
    },
    {
      "type": "aspect",
      "statement": "Sun opposition Saturn, orb 1.4°.",
      "source_refs": ["Sun", "Saturn"]
    }
  ]
}
```

Evidence statements must be generated from structured facts. The AI consumes these statements; it does not rewrite the underlying facts.

## 6. AI Input Contract (Target)
AI should receive:
- report type;
- user name when needed for prose;
- targeted evidence;
- explicit output schema;
- prompt version.

AI should not receive unrelated raw chart data unless there is a documented reason.

## 7. AI Output Contract
For structured products, prefer JSON:
```json
{
  "status": "success",
  "type": "natal_7",
  "report": "...",
  "sections": [],
  "schema_version": "1.0",
  "prompt_version": "1.0"
}
```

If a report contains metrics, validate their range and type before returning them to the frontend.

## 8. Cache Contract
Chart cache key must be based on normalized birth input and calculation/config version.

AI cache key must include:
- chart identity;
- report type;
- package/mode when it changes output;
- question for Q&A;
- prompt version;
- evidence/schema version when output semantics depend on it.

A stale cache must never masquerade as a fresh calculation after an intentional rule/schema change.
