from __future__ import annotations

from chart_schema import (
    BirthData,
    ChartSettings,
    NormalizedChart,
    NatalChart,
)
from evidence_integration import build_evidence_snapshot, candidate_to_evidence, get_pattern_evidence
from pattern_schema import PatternCandidate, PatternEngineResult, PatternRanking, PatternScore, PatternSignal


def make_chart() -> NormalizedChart:
    birth = BirthData(
        date="1990-01-01",
        time="12:00",
        location_name="Bangkok",
        latitude=13.7563,
        longitude=100.5018,
        timezone="Asia/Bangkok",
    )
    natal = NatalChart(
        birth_data=birth,
        settings=ChartSettings(),
        planets={},
        angles={},
        houses={},
    )
    return NormalizedChart(natal=natal)


def make_candidate() -> PatternCandidate:
    signal = PatternSignal(
        signal_id="western:aspect:Sun/Saturn",
        domain="western",
        type="aspect",
        source="Sun/Saturn",
        detail="Sun □ Saturn (square, orb 1.200°)",
        weight=0.9,
        orb=1.2,
        factors=["Sun", "Saturn", "square"],
        independent_key="aspect:Sun/Saturn",
    )
    score = PatternScore(
        western=0.9,
        uranian=0,
        context=0,
        specificity=0.35,
        signal_count=1,
        total=1.25,
    )
    return PatternCandidate(
        pattern_id="P02",
        name="Perfectionism",
        life_question="อะไรทำให้ฉันรู้สึกว่ายังไม่ดีพอ?",
        score=score,
        signals=[signal],
        validation_route="P02",
    )


def test_candidate_maps_to_traceable_evidence():
    block = candidate_to_evidence(make_candidate())
    assert block.pattern_id == "P02"
    assert block.evidence_count == 1
    item = block.evidence[0]
    assert item.statement.startswith("Sun")
    assert item.source_refs[:2] == ["Sun", "Saturn"]
    assert item.weight == 0.9


def test_snapshot_binds_versions_and_filters_patterns():
    candidate = make_candidate()
    result = PatternEngineResult(
        engine_version="t6.1",
        pattern_library_version="v1",
        ranking=PatternRanking(candidates=[candidate]),
    )
    snapshot = build_evidence_snapshot(make_chart(), result, pattern_ids=["P02"])

    assert snapshot.engine_version == "t7.1"
    assert snapshot.source_pattern_engine_version == "t6.1"
    assert snapshot.pattern_library_version == "v1"
    assert snapshot.chart_schema_version == "1.0"
    assert get_pattern_evidence(snapshot, "P02") is not None
    assert get_pattern_evidence(snapshot, "P01") is None
