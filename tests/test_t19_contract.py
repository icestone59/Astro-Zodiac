from datetime import datetime, timezone
from uuid import uuid4
from persistence_factory import persistence_mode
from postgres_membership_repository import PostgresMembershipRepository

class FakeCursor:
    def __init__(self, rows=()): self.rows=list(rows); self.calls=[]
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def execute(self, sql, params): self.calls.append((sql,params))
    def fetchall(self): return self.rows

class FakeConn:
    def __init__(self, rows=()): self.c=FakeCursor(rows)
    def cursor(self): return self.c

def test_membership_reader_maps_active_grant():
    uid=uuid4(); mid=uuid4(); now=datetime.now(timezone.utc)
    c=FakeConn([(str(mid),str(uid),'action_plan_599','active','payment',now,None,'ord-1')])
    s=PostgresMembershipRepository(c).get_state(uid, now=now)
    assert s.active_products == ['free','action_plan_599']
    assert s.has_product('action_plan_599', now=now)

def test_default_runtime_mode_is_safe_dev(monkeypatch):
    monkeypatch.delenv('ASTRO_ZODIAC_PERSISTENCE', raising=False)
    assert persistence_mode() == 'memory'

def test_inactive_or_expired_grant_is_not_returned():
    uid=uuid4(); now=datetime.now(timezone.utc)
    c=FakeConn([])
    s=PostgresMembershipRepository(c).get_state(uid, now=now)
    assert s.active_products == ['free']
