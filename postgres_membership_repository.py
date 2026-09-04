"""T19 PostgreSQL membership reader for T12/T13 entitlement decisions."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from membership_schema import MembershipGrant, MembershipState


class PostgresMembershipRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_state(self, user_id: UUID, now: datetime | None = None) -> MembershipState:
        now = now or datetime.now(timezone.utc)
        grants: list[MembershipGrant] = []
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT membership_id,user_id,product_id,status,source,starts_at,ends_at,external_reference FROM membership_grants WHERE user_id = %s AND status = 'active' AND starts_at <= %s AND (ends_at IS NULL OR ends_at > %s)",
                (str(user_id), now, now),
            )
            for row in cur.fetchall():
                grants.append(MembershipGrant(
                    membership_id=UUID(str(row[0])), user_id=UUID(str(row[1])), product_id=row[2],
                    status=row[3], source=row[4], starts_at=row[5], ends_at=row[6], external_reference=row[7]
                ))
        products = ['free'] + [g.product_id for g in grants if g.product_id != 'free']
        return MembershipState(user_id=user_id, active_products=list(dict.fromkeys(products)), grants=grants)
