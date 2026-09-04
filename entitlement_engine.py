"""Astro-Zodiac T12 — deterministic entitlement engine.

No payment provider, auth system, or persistence is wired here. This is the
pure domain layer that downstream API/auth/billing code can call.
"""
from __future__ import annotations

from product_catalog import get_product
from product_schema import AccessDecision, FeatureId, ProductId, UserProductState


def has_product(state: UserProductState, product_id: ProductId) -> bool:
    return product_id in state.active_products


def _effective_product(state: UserProductState, feature: FeatureId) -> ProductId:
    # Professional is intentionally a separate product line. For each feature,
    # choose the most specific active product instead of relying on price order.
    candidates: list[ProductId] = [
        "astro_professional_1999",
        "action_plan_599",
        "personal_insight_99",
        "free",
    ]
    for product_id in candidates:
        if has_product(state, product_id) and get_product(product_id).features.get(feature, False):
            return product_id
    return "free"


def check_access(state: UserProductState, feature: FeatureId) -> AccessDecision:
    product_id = _effective_product(state, feature)
    allowed = get_product(product_id).features.get(feature, False)
    if allowed:
        reason = f"feature granted by active product {product_id}"
    else:
        reason = f"feature not included in active products; nearest product is {product_id}"
    quota = get_product(product_id).ai_quota.questions if feature in {"ai_personal_insight", "ai_life_planning"} else None
    return AccessDecision(
        allowed=allowed,
        product_id=product_id,
        feature=feature,
        reason=reason,
        ai_remaining=quota,
    )


def check_ai_quota(state: UserProductState, feature: FeatureId, used_questions: int) -> AccessDecision:
    if used_questions < 0:
        raise ValueError("used_questions cannot be negative")
    decision = check_access(state, feature)
    if not decision.allowed:
        return decision.model_copy(update={"ai_remaining": 0, "reason": "AI feature is not entitled"})
    quota = get_product(decision.product_id).ai_quota.questions
    if quota is None:
        return decision.model_copy(update={"ai_remaining": None, "reason": "AI quota is not locked for this product"})
    remaining = max(quota - used_questions, 0)
    return decision.model_copy(update={"allowed": remaining > 0, "ai_remaining": remaining,
                                       "reason": "AI quota available" if remaining > 0 else "AI quota exhausted"})
