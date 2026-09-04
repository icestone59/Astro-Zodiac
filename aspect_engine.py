"""
Astro-Zodiac T4 — Natal Aspect Engine

Deterministic aspect calculation from the normalized chart.
No AI interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from chart_schema import Aspect, ChartPoint

MAJOR_ASPECTS: Tuple[Tuple[str, float], ...] = (
    ("conjunction", 0.0),
    ("sextile", 60.0),
    ("square", 90.0),
    ("trine", 120.0),
    ("opposition", 180.0),
)

DEFAULT_ORBS = {
    "Sun": 8.0,
    "Moon": 8.0,
    "Mercury": 6.0,
    "Venus": 6.0,
    "Mars": 6.0,
    "Jupiter": 7.0,
    "Saturn": 7.0,
    "Uranus": 6.0,
    "Neptune": 6.0,
    "Pluto": 6.0,
    "Chiron": 5.0,
    "NorthNode": 5.0,
}

ASPECT_SYMBOLS = {
    "conjunction": "☌",
    "sextile": "✶",
    "square": "□",
    "trine": "△",
    "opposition": "☍",
}


def circular_distance(a: float, b: float) -> float:
    """Smallest absolute angular distance between two longitudes."""
    delta = abs((float(a) - float(b)) % 360.0)
    return min(delta, 360.0 - delta)


def normalize_aspect_angle(a: float, b: float) -> float:
    """
    Return the smaller angle, useful for aspect matching.
    """
    return circular_distance(a, b)


def _aspect_orb(p1: ChartPoint, p2: ChartPoint, aspect_name: str,
                custom_orbs: Optional[dict] = None) -> float:
    """
    Use the larger of the two participating point orbs by default.
    A later settings layer can replace this with per-aspect/per-point policy.
    """
    orbs = dict(DEFAULT_ORBS)
    if custom_orbs:
        orbs.update(custom_orbs)
    return max(orbs.get(p1.name, 5.0), orbs.get(p2.name, 5.0))


def find_aspect(
    p1: ChartPoint,
    p2: ChartPoint,
    *,
    custom_orbs: Optional[dict] = None,
) -> Optional[Aspect]:
    """
    Return a major natal aspect if within configured orb, else None.

    Applying/separating is left None in T4 because a robust determination
    requires consistent speed semantics and a defined policy for angles/nodes.
    """
    separation = normalize_aspect_angle(p1.degree_raw, p2.degree_raw)

    best = None
    best_abs_error = None

    for name, exact in MAJOR_ASPECTS:
        error = abs(separation - exact)
        orb = _aspect_orb(p1, p2, name, custom_orbs)
        if error <= orb:
            if best_abs_error is None or error < best_abs_error:
                best = (name, exact, error)
                best_abs_error = error

    if best is None:
        return None

    name, exact, error = best
    return Aspect(
        p1=p1.name,
        p2=p2.name,
        aspect=name,
        symbol=ASPECT_SYMBOLS[name],
        exact_angle=exact,
        orb=round(error, 6),
        applying=None,
    )


def calculate_major_aspects(
    points: Sequence[ChartPoint],
    *,
    custom_orbs: Optional[dict] = None,
) -> List[Aspect]:
    """
    Calculate unique pairwise major aspects.
    """
    aspects: List[Aspect] = []

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            aspect = find_aspect(
                points[i],
                points[j],
                custom_orbs=custom_orbs,
            )
            if aspect is not None:
                aspects.append(aspect)

    aspects.sort(key=lambda a: (a.aspect, a.orb, a.p1, a.p2))
    return aspects


def calculate_natal_aspects(
    planets: dict,
    *,
    custom_orbs: Optional[dict] = None,
    include_uranian_factors: bool = False,
) -> List[Aspect]:
    """
    Convenience wrapper for normalized chart planet mapping.

    By default, Uranian hypothetical factors are excluded from the main natal
    major-aspect set. Their dedicated engine will handle 90°/midpoint logic.
    """
    selected: List[ChartPoint] = []

    for name, point in planets.items():
        if not include_uranian_factors and point.point_type == "uranian":
            continue
        selected.append(point)

    return calculate_major_aspects(
        selected,
        custom_orbs=custom_orbs,
    )
