from datetime import datetime, timezone, timedelta
from uuid import uuid4

from auth_security import hash_password
from postgres_auth_repository import PostgresAuthRepository
from user_schema import UserAccount


class FakeCursor:
    def __init__(self, responses):
        self.responses = list(responses)
        self.sql = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params

    def fetchone(self):
        return self.responses.pop(0)


class FakeConn:
    def __init__(self, responses):
        self.cursor_obj = FakeCursor(responses)

    def cursor(self):
        return self.cursor_obj


def test_get_user_uses_user_id_schema():
    uid = uuid4()
    now = datetime.now(timezone.utc)
    conn = FakeConn([(
        uid, "test@example.com", "Tester", "user", "active",
        False, now, None
    )])
    repo = PostgresAuthRepository(conn)
    user = repo.get_user(uid)

    assert user is not None
    assert user.user_id == uid
    assert str(user.email) == "test@example.com"
    assert "WHERE user_id = %s" in conn.cursor_obj.sql


def test_get_password_hash_uses_user_id():
    uid = uuid4()
    password_hash = hash_password("correct-password")
    conn = FakeConn([(password_hash,)])
    repo = PostgresAuthRepository(conn)

    assert repo.get_password_hash(uid) == password_hash
    assert "WHERE user_id = %s" in conn.cursor_obj.sql


def test_session_lookup_rejects_missing_row():
    conn = FakeConn([None])
    repo = PostgresAuthRepository(conn)
    assert repo.get_session_user("missing", datetime.now(timezone.utc)) is None


def test_session_lookup_returns_user_id():
    uid = uuid4()
    conn = FakeConn([(uid,)])
    repo = PostgresAuthRepository(conn)

    resolved = repo.get_session_user(
        "token-hash",
        datetime.now(timezone.utc),
    )
    assert resolved == uid
