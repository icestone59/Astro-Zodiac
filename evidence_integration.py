"""Astro-Zodiac T7 — deterministic Evidence Engine Integration.

The module converts T6 PatternSignal objects into traceable evidence items.
It does not calculate astrology, infer psychology, or generate interpretation.
The existing legacy evidence_engine.py is intentionally left untouched; this
adapter establishes the new contract without forcing a risky main.py rewrite.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from chart_schema import NormalizedChart
from evidence_schema import EvidenceItem, EvidenceSnapshot, PatternEvidence
from pattern_schema import PatternCandidate, PatternEngineResult, PatternSignal

_ENGINE_VERSION = "t7.1"
_TYPE_MAP = {
    "aspect": "aspect",
    "house_context": "house_context",
    "house_ruler": "house_ruler",
    "sign_context": "sign_context",
    "planetary_picture": "planetary_picture",
    "90_degree_structure": "90_degree_structure",
    "supportive_aspect": "supportive_aspect",
    "agency_context": "agency_context",
}


def _source_refs(signal: PatternSignal) -> List[str]:
    """Return stable fact references from the T6 signal factors."""
    if signal.factors:
        return list(dict.fromkeys(signal.factors))
    return [signal.source]


def signal_to_evidence(pattern_id: str, signal: PatternSignal, index: int) -> EvidenceItem:
    """Translate one T6 deterministic signal into one traceable evidence item."""
    evidence_type = _TYPE_MAP.get(signal.type)
    if evidence_type is None:
        raise ValueError(f"Unsupported PatternSignal type: {signal.type}")

    evidence_id = f"{pattern_id}:{signal.signal_id}:{index}"
    return EvidenceItem(
        evidence_id=evidence_id,
        pattern_id=pattern_id,
        signal_id=signal.signal_id,
        domain=signal.domain,
        type=evidence_type,
        statement=signal.detail,
        source_refs=_source_refs(signal),
        factors=list(signal.factors),
        weight=signal.weight,
        orb=signal.orb,
    )


def candidate_to_evidence(candidate: PatternCandidate) -> PatternEvidence:
    """Build a deterministic evidence block for one Pattern Candidate."""
    evidence = [
        signal_to_evidence(candidate.pattern_id, signal, index)
        for index, signal in enumerate(candidate.signals)
    ]
    domains = list(dict.fromkeys(item.domain for item in evidence))
    return PatternEvidence(
        pattern_id=candidate.pattern_id,
        evidence=evidence,
        evidence_count=len(evidence),
        evidence_weight_total=round(sum(item.weight for item in evidence), 6),
        domains_present=domains,
    )


def build_evidence_snapshot(
    chart: NormalizedChart,
    pattern_result: PatternEngineResult,
    *,
    pattern_ids: Optional[Sequence[str]] = None,
) -> EvidenceSnapshot:
    """Create a versioned evidence snapshot from chart + T6 result.

    `chart` is used only to bind the snapshot to the canonical chart schema
    version. All evidence facts come from T6 structured signals.
    """
    selected = set(pattern_ids) if pattern_ids is not None else None
    candidates: Iterable[PatternCandidate] = pattern_result.ranking.candidates
    pattern_blocks: List[PatternEvidence] = []

    for candidate in candidates:
        if selected is not None and candidate.pattern_id not in selected:
            continue
        pattern_blocks.append(candidate_to_evidence(candidate))

    return EvidenceSnapshot(
        schema_version="1.0",
        engine_version=_ENGINE_VERSION,
        source_pattern_engine_version=pattern_result.engine_version,
        pattern_library_version=pattern_result.pattern_library_version,
        chart_schema_version=chart.schema_version,
        patterns=pattern_blocks,
    )


def get_pattern_evidence(
    snapshot: EvidenceSnapshot,
    pattern_id: str,
) -> Optional[PatternEvidence]:
    """Return one pattern's evidence block, or None when absent."""
    for block in snapshot.patterns:
        if block.pattern_id == pattern_id:
            return block
    return None
