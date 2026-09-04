from __future__ import annotations
from typing import Sequence
from application_schema import AccessResponse, BirthChartRequest, CurrentUserResponse, PatternAnalysisResponse
from astro_calc import calculate_natal_chart
from aspect_engine import calculate_natal_aspects
from action_plan_engine import build_action_plan
from action_plan_schema import ActionPlan, GoalContext
from entitlement_engine import check_access
from evidence_integration import build_evidence_snapshot
from house_ruler_engine import attach_house_rulers
from membership_schema import MembershipState
from pattern_engine import calculate_patterns
from psychology_engine import recommend_psychology
from psychology_schema import PsychologyContext
from tracking_engine import create_tracking_session
from tracking_schema import BaselineMetrics, TrackingSession
from validation_engine import create_validation_session
from validation_schema import BehavioralEvidence, QuestionResponse

_ENGINE_PIPELINE_VERSION = "t16.1"

def prepare_chart(request: BirthChartRequest):
    chart = calculate_natal_chart(request.day, request.month, request.year_buddhist, request.hour, request.minute, request.location_name)
    natal = attach_house_rulers(chart.natal)
    natal = natal.model_copy(update={"aspects": calculate_natal_aspects(natal.planets)})
    return chart.model_copy(update={"natal": natal})

def analyze_free(request: BirthChartRequest, *, pattern_ids: Sequence[str] | None = None) -> PatternAnalysisResponse:
    chart = prepare_chart(request)
    result = calculate_patterns(chart, mvp_only=True)
    evidence = build_evidence_snapshot(chart, result, pattern_ids=pattern_ids)
    return PatternAnalysisResponse(chart=chart, pattern_result=result, evidence_snapshot=evidence)

def validate_candidate(candidate, responses: Sequence[QuestionResponse], behavioral_evidence: Sequence[BehavioralEvidence] = (), behavioral_example_text: str | None = None):
    return create_validation_session(candidate, responses=responses, behavioral_evidence=behavioral_evidence, behavioral_example_text=behavioral_example_text)

def build_psychology_for_validated_pattern(pattern_id: str, validation_status: str):
    if validation_status != "validated":
        raise ValueError("psychology recommendation requires validated pattern")
    return recommend_psychology(PsychologyContext(pattern_id=pattern_id, validation_status=validation_status, pattern_fit_score=0.0))

def build_action_plan_for_validated_pattern(pattern_id: str, validation_status: str, goal: str, duration_days: int = 7) -> ActionPlan:
    if validation_status != "validated":
        raise ValueError("action plan requires validated pattern")
    psychology_result = recommend_psychology(PsychologyContext(pattern_id=pattern_id, validation_status=validation_status, pattern_fit_score=0.0))
    goal_context = GoalContext(goal_statement=goal, preferred_duration_days=duration_days)
    return build_action_plan(psychology_result, goal_context)

def start_tracking(action_plan: ActionPlan, baseline: BaselineMetrics | None = None) -> TrackingSession:
    return create_tracking_session(action_plan, baseline=baseline)

def check_feature_access(state: MembershipState, feature: str) -> AccessResponse:
    decision = check_access(state, feature)
    return AccessResponse(allowed=decision.allowed, product_id=decision.product_id, feature=feature, reason=decision.reason, ai_remaining=decision.ai_remaining)

def current_user(user, membership: MembershipState) -> CurrentUserResponse:
    return CurrentUserResponse(user_id=user.user_id, email=str(user.email), display_name=user.display_name, role=user.role, status=user.status, product_ids=list(membership.active_products))

def pipeline_version() -> str:
    return _ENGINE_PIPELINE_VERSION
