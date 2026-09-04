from entitlement_engine import check_access, check_ai_quota
from product_schema import UserProductState


def test_free_gate_and_99_ai_quota():
    state = UserProductState(active_products=["free"])
    assert check_access(state, "pattern_top3").allowed is True
    assert check_access(state, "pattern_validation").allowed is False
    state99 = UserProductState(active_products=["free", "personal_insight_99"])
    assert check_ai_quota(state99, "ai_personal_insight", 2).allowed is True
    assert check_ai_quota(state99, "ai_personal_insight", 3).allowed is False


def test_599_unlocks_action_and_tracking():
    state = UserProductState(active_products=["free", "personal_insight_99", "action_plan_599"])
    assert check_access(state, "psychology_intervention").allowed is True
    assert check_access(state, "tracking").allowed is True
    assert check_ai_quota(state, "ai_life_planning", 9).ai_remaining == 1


def test_professional_is_separate_line():
    state = UserProductState(active_products=["astro_professional_1999"])
    assert check_access(state, "natal_full").allowed is True
    assert check_access(state, "evidence_matrix").allowed is True
    assert check_access(state, "action_plan").allowed is False
    assert check_ai_quota(state, "ai_personal_insight", 0).ai_remaining is None
