"""Astro-Zodiac T6 — deterministic Pattern Engine.

Inputs: NormalizedChart + T3 house rulers + T4 natal aspects + T5 Uranian signals.
Output: Pattern candidates and Free-product ranking (primary, secondary, strength).

This engine only discovers/organizes exploratory astrological signals.  It does
not diagnose, infer childhood causes, or generate natural-language interpretation.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from chart_schema import NormalizedChart
from pattern_library import PatternDefinition, get_mvp_patterns, pair
from pattern_schema import PatternCandidate, PatternEngineResult, PatternRanking, PatternScore, PatternSignal
from uranian_engine import calculate_planetary_pictures, calculate_90_degree_positions


ASPECT_STRENGTH = {
    "conjunction": 1.00,
    "opposition": 0.95,
    "square": 0.90,
    "trine": 0.75,
    "sextile": 0.65,
}


def _point(chart: NormalizedChart, name: str):
    return chart.natal.planets.get(name) or chart.natal.angles.get(name)


def _all_points(chart: NormalizedChart):
    points = list(chart.natal.planets.values())
    points.extend(chart.natal.angles.values())
    return points


def _aspect_pair_match(aspect, wanted: Tuple[str, str]) -> bool:
    return pair(aspect.p1, aspect.p2) == wanted


def _append_signal(bucket: List[PatternSignal], *, domain: str, type_: str, source: str,
                   detail: str, weight: float, factors: Iterable[str], orb: Optional[float] = None,
                   independent_key: Optional[str] = None) -> None:
    signal_id = f"{domain}:{type_}:{source}"
    bucket.append(PatternSignal(
        signal_id=signal_id,
        domain=domain,
        type=type_,
        source=source,
        detail=detail,
        weight=round(weight, 6),
        orb=orb,
        factors=list(factors),
        independent_key=independent_key,
    ))


def _house_context_signals(chart: NormalizedChart, definition: PatternDefinition,
                           signals: List[PatternSignal]) -> None:
    # Direct point-in-house context.
    for point_name, point in chart.natal.planets.items():
        if point.house in definition.relevant_houses:
            weight = 0.55 if point_name in {"Sun", "Moon", "Mercury", "Venus", "Mars", "Saturn"} else 0.35
            _append_signal(
                signals, domain="context", type_="house_context", source=f"{point_name}.house",
                detail=f"{point_name} is in House {point.house}", weight=weight,
                factors=[point_name, f"House {point.house}"],
                independent_key=f"house:{point.house}",
            )

    # Relevant ruler placement/context.
    for house_key, ruler in chart.natal.house_rulers.items():
        if ruler.house in definition.relevant_houses and ruler.ruler_house in definition.relevant_houses:
            _append_signal(
                signals, domain="context", type_="house_ruler", source=house_key,
                detail=f"{house_key} ruler {ruler.ruler_planet} is in House {ruler.ruler_house}",
                weight=0.75, factors=[house_key, ruler.ruler_planet, f"House {ruler.ruler_house}"],
                independent_key=f"ruler:{ruler.house}:{ruler.ruler_house}",
            )

    # Relevant sign context on participating planets.
    if definition.relevant_signs:
        for point_name, point in chart.natal.planets.items():
            if point.sign in definition.relevant_signs:
                _append_signal(
                    signals, domain="context", type_="sign_context", source=f"{point_name}.sign",
                    detail=f"{point_name} is in {point.sign}", weight=0.35,
                    factors=[point_name, point.sign], independent_key=f"sign:{point.sign}",
                )


def _western_signals(chart: NormalizedChart, definition: PatternDefinition) -> List[PatternSignal]:
    signals: List[PatternSignal] = []
    for aspect in chart.natal.aspects:
        p = pair(aspect.p1, aspect.p2)
        if p in definition.aspect_pairs:
            base = 1.0 * ASPECT_STRENGTH.get(aspect.aspect, 0.5)
            # Tightness bonus inside the configured orb.
            tightness = max(0.0, 1.0 - (aspect.orb / 8.0))
            weight = base * (0.7 + 0.3 * tightness)
            _append_signal(
                signals, domain="western", type_="aspect", source=f"{aspect.p1}/{aspect.p2}",
                detail=f"{aspect.p1} {aspect.symbol} {aspect.p2} ({aspect.aspect}, orb {aspect.orb:.3f}°)",
                weight=weight, factors=[aspect.p1, aspect.p2, aspect.aspect], orb=aspect.orb,
                independent_key=f"aspect:{p}",
            )
    _house_context_signals(chart, definition, signals)
    return signals


def _uranian_signals(chart: NormalizedChart, definition: PatternDefinition) -> List[PatternSignal]:
    signals: List[PatternSignal] = []
    points = _all_points(chart)
    if not points:
        return signals

    pictures = calculate_planetary_pictures(points, orb=1.0)
    for picture in pictures:
        factors = pair(picture["a"], picture["b"])
        c = picture["c"]
        # Relevant A/B pair plus relevant target factor/angle.
        if factors in definition.uranian_pairs and (c in {"ASC", "MC"} or c in {p.name for p in points}):
            _append_signal(
                signals, domain="uranian", type_="planetary_picture", source=picture["picture"],
                detail=f"{picture['picture']} on 90° dial (orb {picture['orb']:.3f}°)",
                weight=max(0.0, 1.2 - picture["orb"]), factors=[picture["a"], picture["b"], c],
                orb=picture["orb"], independent_key=f"picture:{factors}:{c}",
            )

    # Use 90° positions to add a deterministic hard-structure signal.  Keep it
    # secondary to explicit pictures to avoid counting every pair too strongly.
    dial = calculate_90_degree_positions(points)
    by_factor = dict(dial)
    for a, b in definition.uranian_pairs:
        if a not in by_factor or b not in by_factor:
            continue
        delta = abs(by_factor[a] - by_factor[b])
        delta = min(delta, 90.0 - delta)
        if delta <= 1.0:
            _append_signal(
                signals, domain="uranian", type_="90_degree_structure", source=f"{a}/{b}",
                detail=f"{a} and {b} align on the 90° dial ({delta:.3f}°)",
                weight=max(0.0, 0.85 - delta * 0.25), factors=[a, b], orb=delta,
                independent_key=f"dial:{a}:{b}",
            )
    return signals


def _score(signals: Sequence[PatternSignal]) -> PatternScore:
    western = sum(s.weight for s in signals if s.domain == "western")
    uranian = sum(s.weight for s in signals if s.domain == "uranian")
    context = sum(s.weight for s in signals if s.domain == "context")
    independent = {s.independent_key for s in signals if s.independent_key}
    signal_count = len(signals)
    specificity = min(2.0, len(independent) * 0.35)
    # Product scoring only — not a psychometric confidence score.
    total = min(10.0, western + uranian + context + specificity)
    return PatternScore(
        western=round(western, 4), uranian=round(uranian, 4), context=round(context, 4),
        specificity=round(specificity, 4), signal_count=signal_count, total=round(total, 4),
    )


def _candidate(chart: NormalizedChart, definition: PatternDefinition) -> PatternCandidate:
    signals = _western_signals(chart, definition)
    signals.extend(_uranian_signals(chart, definition))
    score = _score(signals)
    return PatternCandidate(
        pattern_id=definition.pattern_id,
        name=definition.name,
        life_question=definition.life_question,
        score=score,
        signals=signals,
        validation_route=definition.validation_route,
    )


def _strength_candidate(chart: NormalizedChart, candidates: Sequence[PatternCandidate]) -> Optional[PatternCandidate]:
    definition = next((d for d in get_mvp_patterns() if d.pattern_id == "P05"), None)
    if definition is None:
        return None
    # Reuse deterministic P05 evidence but only surface it as a strength when
    # supportive Sun/Jupiter or agency-related evidence is present.
    signals: List[PatternSignal] = []
    for aspect in chart.natal.aspects:
        if pair(aspect.p1, aspect.p2) == pair("Sun", "Jupiter"):
            _append_signal(
                signals, domain="western", type_="supportive_aspect", source="Sun/Jupiter",
                detail=f"Sun {aspect.symbol} Jupiter ({aspect.aspect}, orb {aspect.orb:.3f}°)",
                weight=1.0 * ASPECT_STRENGTH.get(aspect.aspect, 0.5),
                factors=["Sun", "Jupiter", aspect.aspect], orb=aspect.orb,
                independent_key="strength:Sun/Jupiter",
            )
    sun = _point(chart, "Sun")
    if sun and sun.house in {1, 10}:
        _append_signal(
            signals, domain="context", type_="agency_context", source="Sun.house",
            detail=f"Sun is in House {sun.house}", weight=0.65, factors=["Sun", f"House {sun.house}"],
            independent_key=f"strength:Sun.house:{sun.house}",
        )
    if not signals:
        return None
    score = _score(signals)
    return PatternCandidate(
        pattern_id="S01",
        name="Agency / Capability Potential",
        life_question="ฉันใช้ศักยภาพของตัวเองได้เต็มที่แค่ไหน?",
        kind="strength",
        score=score,
        signals=signals,
        validation_route="STRENGTH",
    )


def rank_patterns(candidates: Sequence[PatternCandidate], strength: Optional[PatternCandidate]) -> PatternRanking:
    ranked = sorted(candidates, key=lambda c: (-c.score.total, c.pattern_id))
    primary = ranked[0] if ranked else None
    secondary = ranked[1] if len(ranked) > 1 else None
    if primary is not None:
        primary = primary.model_copy(update={"kind": "blind_spot"})
    if secondary is not None:
        secondary = secondary.model_copy(update={"kind": "secondary"})
    return PatternRanking(primary=primary, secondary=secondary, strength=strength, candidates=ranked)


def calculate_patterns(chart: NormalizedChart, *, mvp_only: bool = True) -> PatternEngineResult:
    """Calculate deterministic pattern candidates and Free Top-3 ranking."""
    definitions = get_mvp_patterns() if mvp_only else tuple(get_mvp_patterns())
    candidates = [_candidate(chart, definition) for definition in definitions]
    strength = _strength_candidate(chart, candidates)
    return PatternEngineResult(ranking=rank_patterns(candidates, strength))
