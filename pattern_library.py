"""Astro-Zodiac T6 — Data-driven Pattern Library v1.

The library describes exploratory mappings only.  It does not claim that an
astrological factor causes a psychological or behavioral outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Tuple


@dataclass(frozen=True)
class PatternDefinition:
    pattern_id: str
    name: str
    life_question: str
    validation_route: str
    allowed_in_mvp: bool
    # Planets that form relevant aspect pairs for the pattern.
    aspect_pairs: FrozenSet[Tuple[str, str]] = frozenset()
    # House numbers where direct planet/context presence can support the pattern.
    relevant_houses: FrozenSet[int] = frozenset()
    # Optional signs that add contextual support when the relevant planet is there.
    relevant_signs: FrozenSet[str] = frozenset()
    # Midpoint/planetary-picture pair labels, normalized alphabetically.
    uranian_pairs: FrozenSet[Tuple[str, str]] = frozenset()
    # Positive-strength mode: used only for the dedicated strength candidate.
    strength_signal_pairs: FrozenSet[Tuple[str, str]] = frozenset()
    strength_planets: FrozenSet[str] = frozenset()



def pair(a: str, b: str) -> Tuple[str, str]:
    return tuple(sorted((a, b)))


PATTERN_LIBRARY_VERSION = "v1"

PATTERN_LIBRARY: Dict[str, PatternDefinition] = {
    "P01": PatternDefinition(
        "P01", "Procrastination / Action Delay",
        "อะไรทำให้ฉันรู้ว่าต้องทำ แต่ยังไม่ลงมือ?", "P01", True,
        aspect_pairs=frozenset({pair("Mars", "Saturn"), pair("Mercury", "Mars")}),
        relevant_houses=frozenset({6, 10, 12}),
        uranian_pairs=frozenset({pair("Mars", "Saturn"), pair("Mercury", "Mars")}),
    ),
    "P02": PatternDefinition(
        "P02", "Perfectionism",
        "อะไรทำให้ฉันรู้สึกว่ายังไม่ดีพอ?", "P02", True,
        aspect_pairs=frozenset({pair("Mercury", "Saturn"), pair("Sun", "Saturn")}),
        relevant_houses=frozenset({6, 10}),
        relevant_signs=frozenset({"Virgo"}),
        uranian_pairs=frozenset({pair("Saturn", "Mercury"), pair("Saturn", "Sun")}),
    ),
    "P03": PatternDefinition(
        "P03", "Decision Avoidance / Indecisiveness",
        "อะไรทำให้ฉันลังเลหรือตัดสินใจช้า?", "P03", True,
        aspect_pairs=frozenset({pair("Mercury", "Saturn"), pair("Mercury", "Neptune")}),
        relevant_houses=frozenset({7}),
        relevant_signs=frozenset({"Libra"}),
        uranian_pairs=frozenset({pair("Mercury", "Saturn"), pair("Mercury", "Neptune")}),
    ),
    "P04": PatternDefinition(
        "P04", "Fear of Failure",
        "ฉันหลีกเลี่ยงอะไรเพราะกลัวพลาด?", "P04", False,
        aspect_pairs=frozenset({pair("Sun", "Saturn"), pair("Mars", "Saturn")}),
        relevant_houses=frozenset({10}),
        uranian_pairs=frozenset({pair("Sun", "Saturn"), pair("Mars", "Saturn")}),
    ),
    "P05": PatternDefinition(
        "P05", "Low Self-Efficacy / Low Confidence",
        "ฉันเชื่อไหมว่าตัวเองรับมือเรื่องยากได้?", "P05", True,
        aspect_pairs=frozenset({pair("Sun", "Saturn"), pair("Sun", "Jupiter")}),
        relevant_houses=frozenset({1, 10}),
        uranian_pairs=frozenset({pair("Sun", "Saturn"), pair("Sun", "Jupiter")}),
        strength_signal_pairs=frozenset({pair("Sun", "Jupiter")}),
        strength_planets=frozenset({"Sun", "Jupiter", "Mars"}),
    ),
    "P06": PatternDefinition(
        "P06", "Values / Direction Confusion",
        "ฉันกำลังใช้ชีวิตตามสิ่งที่ตัวเองต้องการจริง ๆ หรือเปล่า?", "P06", True,
        aspect_pairs=frozenset({pair("Sun", "NorthNode"), pair("Sun", "Neptune")}),
        relevant_houses=frozenset({9, 10}),
        uranian_pairs=frozenset({pair("Sun", "NorthNode"), pair("Sun", "Neptune")}),
    ),
    "P07": PatternDefinition(
        "P07", "Goal Failure",
        "ทำไมฉันตั้งเป้าหมายได้ แต่ทำต่อไม่ได้?", "P07", False,
        aspect_pairs=frozenset({pair("Mars", "Saturn"), pair("Jupiter", "Saturn")}),
        relevant_houses=frozenset({6, 10}),
        uranian_pairs=frozenset({pair("Mars", "Saturn"), pair("Jupiter", "Saturn")}),
    ),
    "P08": PatternDefinition(
        "P08", "Rumination / Thinking Loop",
        "ทำไมฉันคิดเรื่องเดิมซ้ำ ๆ จนลงมือช้า?", "P08", True,
        aspect_pairs=frozenset({pair("Mercury", "Neptune"), pair("Mercury", "Saturn"), pair("Moon", "Mercury")}),
        relevant_houses=frozenset({3, 8, 12}),
        uranian_pairs=frozenset({pair("Mercury", "Neptune"), pair("Mercury", "Saturn"), pair("Mercury", "Moon")}),
    ),
    "P09": PatternDefinition(
        "P09", "Avoidance / Comfort Zone",
        "อะไรที่ฉันรู้ว่าควรเผชิญ แต่ยังหลีกเลี่ยง?", "P09", False,
        aspect_pairs=frozenset({pair("Mars", "Saturn"), pair("Saturn", "Neptune")}),
        relevant_houses=frozenset({6, 8, 12}),
        uranian_pairs=frozenset({pair("Mars", "Saturn"), pair("Mars", "Neptune")}),
    ),
    "P10": PatternDefinition(
        "P10", "People-Pleasing / Boundary Difficulty",
        "ฉันกำลังใช้ชีวิตตามความต้องการของคนอื่นมากกว่าของตัวเองหรือไม่?", "P10", False,
        aspect_pairs=frozenset({pair("Venus", "Saturn"), pair("Moon", "Saturn"), pair("Venus", "Neptune")}),
        relevant_houses=frozenset({4, 7}),
        relevant_signs=frozenset({"Libra"}),
        uranian_pairs=frozenset({pair("Venus", "Saturn"), pair("Moon", "Saturn"), pair("Venus", "Neptune")}),
    ),
    "P11": PatternDefinition(
        "P11", "Emotional Reactivity",
        "เวลารู้สึกแรง ฉันตอบสนองก่อนคิดหรือไม่?", "P11", False,
        aspect_pairs=frozenset({pair("Moon", "Mars"), pair("Moon", "Uranus"), pair("Mars", "Uranus"), pair("Moon", "Pluto")}),
        relevant_houses=frozenset({1, 4}),
        uranian_pairs=frozenset({pair("Moon", "Mars"), pair("Moon", "Uranus"), pair("Mars", "Uranus"), pair("Moon", "Pluto")}),
    ),
    "P12": PatternDefinition(
        "P12", "Habit Maintenance",
        "ทำไมฉันเริ่มได้ แต่ทำต่อเนื่องไม่ได้?", "P12", False,
        aspect_pairs=frozenset({pair("Mars", "Saturn")}),
        relevant_houses=frozenset({6}),
        uranian_pairs=frozenset({pair("Mars", "Saturn")}),
    ),
}


def get_mvp_patterns() -> Tuple[PatternDefinition, ...]:
    return tuple(PATTERN_LIBRARY[k] for k in ("P01", "P02", "P03", "P05", "P06", "P08"))
