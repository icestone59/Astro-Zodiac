"""
Astro-Zodiac T3 — House Ruler Engine

Deterministically maps:
House cusp sign -> traditional ruler -> ruler placement.

This module intentionally contains no AI interpretation.
"""

from __future__ import annotations

from typing import Dict

from chart_schema import HouseRuler, NatalChart

TRADITIONAL_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


def calculate_house_rulers(chart: NatalChart) -> Dict[str, HouseRuler]:
    """
    Build all 12 house-ruler mappings from an already-calculated natal chart.

    Traditional rulership is used as the MVP default.
    Modern co-rulers are intentionally deferred to a later settings/version.
    """
    result: Dict[str, HouseRuler] = {}

    for house_num in range(1, 13):
        house_key = f"House_{house_num}"
        cusp = chart.houses.get(house_key)
        if cusp is None:
            raise ValueError(f"Missing cusp data for {house_key}")

        ruler_planet = TRADITIONAL_RULERS.get(cusp.sign)
        if ruler_planet is None:
            raise ValueError(f"Unsupported sign: {cusp.sign}")

        ruler = chart.planets.get(ruler_planet)
        if ruler is None:
            raise ValueError(
                f"Required ruler planet '{ruler_planet}' is missing from chart"
            )

        result[house_key] = HouseRuler(
            house=house_num,
            cusp_sign=cusp.sign,
            ruler_planet=ruler_planet,
            ruler_degree_raw=ruler.degree_raw,
            ruler_sign=ruler.sign,
            ruler_house=ruler.house,
            ruler_dms=ruler.dms,
        )

    return result


def attach_house_rulers(chart: NatalChart) -> NatalChart:
    """
    Return a validated copy with house_rulers populated.
    """
    chart.house_rulers = calculate_house_rulers(chart)
    return chart
