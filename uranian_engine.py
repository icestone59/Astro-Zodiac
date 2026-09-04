"""
Astro-Zodiac T5 — Uranian Engine

Deterministic technical layer for:
- 90° dial normalization
- hard-aspect equivalence on the 90° dial
- midpoint calculations
- planetary-picture detection of the form A/B=C

No interpretation is performed here.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, Iterable, List, Optional, Sequence

from chart_schema import ChartPoint


def normalize_90(degree: float) -> float:
    """Fold 0..360 longitude onto a 0..90 dial."""
    return round(float(degree) % 90.0, 6)


def shortest_arc(a: float, b: float) -> float:
    """Return the shortest angular distance in 0..180."""
    delta = abs((float(a) - float(b)) % 360.0)
    return min(delta, 360.0 - delta)


def midpoint_longitude(a: float, b: float) -> float:
    """
    Return the midpoint on the shortest arc between two longitudes.

    For diametrically opposite points there are two equivalent midpoints.
    MVP returns the clockwise midpoint from a to b.
    """
    a = float(a) % 360.0
    b = float(b) % 360.0
    clockwise = (b - a) % 360.0
    if clockwise <= 180.0:
        return (a + clockwise / 2.0) % 360.0
    return (b + ((a - b) % 360.0) / 2.0) % 360.0


def midpoint_axis(a: float, b: float) -> float:
    """
    Canonical midpoint axis on the 90° dial.

    Because A/B and the opposite point represent the same axis in Uranian
    midpoint work, fold the midpoint onto 0..90.
    """
    return normalize_90(midpoint_longitude(a, b))


def axis_distance(a: float, b: float) -> float:
    """Distance between two points on the 90° dial."""
    return min(
        abs(normalize_90(a) - normalize_90(b)),
        90.0 - abs(normalize_90(a) - normalize_90(b)),
    )


def detect_midpoint_picture(
    a: ChartPoint,
    b: ChartPoint,
    c: ChartPoint,
    *,
    orb: float = 1.0,
) -> Optional[dict]:
    """
    Detect A/B=C when C falls on the midpoint axis of A and B.

    The relation is tested on the 90° dial.
    """
    if orb < 0:
        raise ValueError("orb must be non-negative")

    midpoint = midpoint_axis(a.degree_raw, b.degree_raw)
    distance = axis_distance(midpoint, c.degree_raw)

    if distance > orb:
        return None

    return {
        "picture": f"{a.name}/{b.name}={c.name}",
        "a": a.name,
        "b": b.name,
        "c": c.name,
        "midpoint_axis": midpoint,
        "orb": round(distance, 6),
        "dial": 90,
    }


def calculate_midpoints(
    points: Sequence[ChartPoint],
    *,
    min_unique: bool = True,
) -> List[dict]:
    """
    Return every pairwise midpoint axis.

    This returns data only. Pattern ranking is handled elsewhere.
    """
    results: List[dict] = []
    seen = set()

    for a, b in combinations(points, 2):
        axis = midpoint_axis(a.degree_raw, b.degree_raw)
        key = tuple(sorted((a.name, b.name)))
        if min_unique:
            dedupe_key = (key, round(axis, 6))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

        results.append({
            "a": a.name,
            "b": b.name,
            "axis_90": axis,
            "longitude_midpoint": midpoint_longitude(
                a.degree_raw, b.degree_raw
            ),
        })

    results.sort(key=lambda x: (x["axis_90"], x["a"], x["b"]))
    return results


def calculate_planetary_pictures(
    points: Sequence[ChartPoint],
    *,
    orb: float = 1.0,
) -> List[dict]:
    """Find A/B=C pictures among the supplied points."""
    if orb < 0:
        raise ValueError("orb must be non-negative")

    results: List[dict] = []
    for a, b in combinations(points, 2):
        for c in points:
            if c.name in {a.name, b.name}:
                continue

            picture = detect_midpoint_picture(a, b, c, orb=orb)
            if picture is not None:
                results.append(picture)

    results.sort(key=lambda x: (x["orb"], x["picture"]))
    return results


def calculate_90_degree_positions(
    points: Sequence[ChartPoint],
) -> Dict[str, float]:
    """Return each factor's 90° dial position."""
    return {
        point.name: normalize_90(point.degree_raw)
        for point in points
    }
