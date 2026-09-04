"""Astro-Zodiac T12 — data-driven product catalog.

Entitlements live here rather than inside routes/UI code.
"""
from __future__ import annotations

from product_schema import AIQuota, EntitlementSet

CATALOG: dict[str, EntitlementSet] = {
    "free": EntitlementSet(
        product_id="free",
        features={
            "free_discovery": True,
            "pattern_top3": True,
            "full_pattern_evidence": False,
            "pattern_validation": False,
            "ai_personal_insight": False,
            "psychology_intervention": False,
            "action_plan": False,
            "tracking": False,
            "ai_life_planning": False,
            "natal_full": False,
            "house_ruler": False,
            "aspects": False,
            "uranian_full": False,
            "transit_analysis": False,
            "evidence_matrix": False,
            "deep_report": False,
            "client_history": False,
            "report_export": False,
        },
        ai_quota=AIQuota(questions=0),
    ),
    "personal_insight_99": EntitlementSet(
        product_id="personal_insight_99",
        features={
            "free_discovery": True,
            "pattern_top3": True,
            "full_pattern_evidence": True,
            "pattern_validation": True,
            "ai_personal_insight": True,
            "psychology_intervention": False,
            "action_plan": False,
            "tracking": False,
            "ai_life_planning": False,
            "natal_full": False,
            "house_ruler": False,
            "aspects": False,
            "uranian_full": False,
            "transit_analysis": False,
            "evidence_matrix": False,
            "deep_report": False,
            "client_history": False,
            "report_export": False,
        },
        ai_quota=AIQuota(questions=3),
    ),
    "action_plan_599": EntitlementSet(
        product_id="action_plan_599",
        features={
            "free_discovery": True,
            "pattern_top3": True,
            "full_pattern_evidence": True,
            "pattern_validation": True,
            "ai_personal_insight": True,
            "psychology_intervention": True,
            "action_plan": True,
            "tracking": True,
            "ai_life_planning": True,
            "natal_full": False,
            "house_ruler": False,
            "aspects": False,
            "uranian_full": False,
            "transit_analysis": False,
            "evidence_matrix": False,
            "deep_report": False,
            "client_history": False,
            "report_export": False,
        },
        ai_quota=AIQuota(questions=10),
    ),
    "astro_professional_1999": EntitlementSet(
        product_id="astro_professional_1999",
        features={
            "free_discovery": True,
            "pattern_top3": True,
            "full_pattern_evidence": True,
            "pattern_validation": True,
            "ai_personal_insight": True,
            "psychology_intervention": False,
            "action_plan": False,
            "tracking": False,
            "ai_life_planning": False,
            "natal_full": True,
            "house_ruler": True,
            "aspects": True,
            "uranian_full": True,
            "transit_analysis": True,
            "evidence_matrix": True,
            "deep_report": True,
            "client_history": True,
            "report_export": True,
        },
        # Professional AI quota intentionally not locked in T12.
        ai_quota=AIQuota(questions=None),
    ),
}


def get_product(product_id: str) -> EntitlementSet:
    try:
        return CATALOG[product_id]
    except KeyError as exc:
        raise ValueError(f"unknown product_id: {product_id}") from exc
