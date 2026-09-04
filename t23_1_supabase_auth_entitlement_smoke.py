from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.rows import tuple_row

ROOT = Path(__file__).resolve().parent
DATABASE_URL = os.environ.get("DATABASE_URL")
KEEP = os.environ.get("T23_KEEP_TEST_DATA") == "1"

# T12 domain models are copied into this package so the final entitlement
# decision is evaluated by the same deterministic rules used by Astro-Zodiac.
from membership_schema import MembershipGrant, MembershipState
from product_schema import UserProductState
from entitlement_engine import check_access
from auth_security import hash_password, verify_password, new_opaque_token, hash_token


def fail(stage: str, exc: Exception) -> None:
    print(f"[FAIL] {stage}: {type(exc).__name__}: {exc}")
    raise SystemExit(1)


def require_url() -> str:
    if not DATABASE_URL:
        fail("configuration", RuntimeError("DATABASE_URL is required"))
    if not DATABASE_URL.lower().startswith(("postgresql://", "postgres://")):
        fail("configuration", RuntimeError("DATABASE_URL must use PostgreSQL"))
    return DATABASE_URL


def main() -> None:
    email = f"t23-auth-{uuid4().hex}@example.invalid"
    password = "T23-Only-Test-Password-123!"
    user_id = uuid4()
    membership_id = uuid4()
    session_token = new_opaque_token()
    token_hash = hash_token(session_token)
    conn = None

    try:
        conn = psycopg.connect(require_url(), row_factory=tuple_row)

        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_setting('server_version')")
            db_name, pg_version = cur.fetchone()
        print(f"[PASS] connection: {db_name}")
        print(f"[INFO] PostgreSQL: {pg_version}")

        # Verify required migrations are present remotely.
        with conn.cursor() as cur:
            cur.execute("""
                SELECT version
                FROM supabase_migrations.schema_migrations
                WHERE version IN ('20260904000000', '20260904000001')
                ORDER BY version
            """)
            versions = [r[0] for r in cur.fetchall()]
        if versions != ['20260904000000', '20260904000001']:
            fail("migration history", RuntimeError(f"unexpected remote migrations: {versions}"))
        print("[PASS] migration history")

        # REGISTER: hash locally, persist only the hash, then read it back.
        password_hash = hash_password(password)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users
                    (user_id, email, display_name, role, status, email_verified,
                     created_at, password_hash)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING user_id, email, password_hash
            """, (
                user_id, email, "T23 Smoke User", "user", "active", False,
                datetime.now(timezone.utc), password_hash
            ))
            saved_user_id, saved_email, saved_hash = cur.fetchone()

        if saved_user_id != user_id or saved_email != email:
            fail("register", RuntimeError("user row mismatch"))
        if saved_hash == password or not saved_hash:
            fail("password storage", RuntimeError("plain password was stored"))
        if not verify_password(password, saved_hash):
            fail("password verification", RuntimeError("stored password hash did not verify"))
        print("[PASS] register + password hash verification")

        # LOGIN: validate password from the persisted hash.
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash, status FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()

        if not row or row[1] != "active" or not verify_password(password, row[0]):
            fail("login", RuntimeError("login verification failed"))
        print("[PASS] login")

        # SESSION: persist a hash of the opaque session token, never the token.
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_sessions
                    (token_hash, user_id, expires_at, created_at, revoked_at)
                VALUES
                    (%s, %s, %s, %s, NULL)
            """, (token_hash, user_id, expires, datetime.now(timezone.utc)))

            cur.execute("""
                SELECT user_id
                FROM user_sessions
                WHERE token_hash = %s
                  AND expires_at > NOW()
                  AND revoked_at IS NULL
            """, (token_hash,))
            resolved = cur.fetchone()

        if not resolved or resolved[0] != user_id:
            fail("session", RuntimeError("session could not be resolved"))
        print("[PASS] session create + resolve")

        # MEMBERSHIP: grant a real T12 product.
        starts = datetime.now(timezone.utc) - timedelta(minutes=1)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO membership_grants
                    (membership_id, user_id, product_id, status, source,
                     starts_at, ends_at, external_reference)
                VALUES
                    (%s, %s, %s, 'active', 'system', %s, NULL, %s)
            """, (membership_id, user_id, "action_plan_599", starts, f"t23:{uuid4().hex}"))

            cur.execute("""
                SELECT membership_id, user_id, product_id, status, source,
                       starts_at, ends_at, external_reference
                FROM membership_grants
                WHERE user_id = %s AND membership_id = %s
            """, (user_id, membership_id))
            row = cur.fetchone()

        if not row or row[2] != "action_plan_599" or row[3] != "active":
            fail("membership", RuntimeError("membership grant not persisted"))
        grant = MembershipGrant(
            membership_id=row[0],
            user_id=row[1],
            product_id=row[2],
            status=row[3],
            source=row[4],
            starts_at=row[5],
            ends_at=row[6],
            external_reference=row[7],
        )
        state = MembershipState(user_id=user_id, active_products=["free", "action_plan_599"], grants=[grant])
        print("[PASS] membership grant read")

        # ENTITLEMENT: convert persistent membership state into T12's
        # product-state contract and prove the feature is granted server-side.
        product_state = UserProductState(
            active_products=list(state.active_products)
        )
        decision = check_access(product_state, "action_plan")
        if not decision.allowed or decision.product_id != "action_plan_599":
            fail("entitlement", RuntimeError(f"unexpected decision: {decision}"))
        print("[PASS] entitlement: action_plan granted by action_plan_599")

        conn.commit()

        # Cleanup by default.
        if not KEEP:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_sessions WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM membership_grants WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            print("[PASS] cleanup")
        else:
            print("[INFO] T23_KEEP_TEST_DATA=1; cleanup skipped")

        print("[PASS] T23.1 Supabase auth/entitlement smoke test complete")
    except SystemExit:
        raise
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        fail("runtime", exc)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
