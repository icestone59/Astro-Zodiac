from datetime import datetime, timedelta, timezone

from auth_security import hash_password, verify_password
from auth_service import AuthError, authenticate, create_session, register, resolve_session
from in_memory_auth_repository import InMemoryAuthRepository
from membership_schema import MembershipState
from membership_service import check_membership, grant_membership, revoke_membership


def test_password_hash_and_verify():
    encoded = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong", encoded)


def test_register_normalizes_email_and_prevents_duplicates():
    repo = InMemoryAuthRepository()
    user = register(repo, " Test@Example.COM ", "password123", "Test")
    assert str(user.email) == "test@example.com"
    try:
        register(repo, "test@example.com", "password123")
        assert False
    except AuthError as exc:
        assert "already registered" in str(exc)


def test_auth_and_session_roundtrip():
    repo = InMemoryAuthRepository()
    user = register(repo, "user@example.com", "password123")
    assert authenticate(repo, "user@example.com", "password123").user_id == user.user_id
    token = create_session(repo, user.user_id, ttl_hours=1)
    assert resolve_session(repo, token).user_id == user.user_id
    assert resolve_session(repo, "not-a-token") is None


def test_membership_grant_and_revoke():
    repo = InMemoryAuthRepository()
    user = register(repo, "user@example.com", "password123")
    state = MembershipState(user_id=user.user_id)
    assert check_membership(state, "action_plan_599").allowed is False
    grant_membership(state, "action_plan_599", source="payment")
    assert check_membership(state, "action_plan_599").allowed is True
    revoke_membership(state, "action_plan_599")
    assert check_membership(state, "action_plan_599").allowed is False


def test_membership_expiry_is_denied():
    repo = InMemoryAuthRepository()
    user = register(repo, "user@example.com", "password123")
    state = MembershipState(user_id=user.user_id)
    now = datetime.now(timezone.utc)
    grant_membership(state, "action_plan_599", starts_at=now - timedelta(days=2), ends_at=now - timedelta(days=1))
    assert check_membership(state, "action_plan_599").allowed is False
