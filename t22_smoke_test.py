from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parent
DATABASE_URL = os.environ.get("DATABASE_URL")
KEEP = os.environ.get("T22_KEEP_TEST_DATA") == "1"


def fail(stage: str, exc: Exception) -> "NoReturn":
    print(f"[FAIL] {stage}: {type(exc).__name__}: {exc}")
    raise SystemExit(1)


def require_database_url() -> str:
    if not DATABASE_URL:
        fail("configuration", RuntimeError("DATABASE_URL is required"))
    if not DATABASE_URL.lower().startswith(("postgresql://", "postgres://")):
        fail("configuration", RuntimeError("DATABASE_URL must be a PostgreSQL URL"))
    return DATABASE_URL


def connect():
    url = require_database_url()
    return psycopg.connect(url, row_factory=dict_row)


def apply_migrations(conn):
    migration_paths = [
        ROOT / "migrations" / "001_initial_postgres.sql",
        ROOT / "migrations" / "002_auth_runtime.sql",
    ]
    missing = [str(p) for p in migration_paths if not p.exists()]
    if missing:
        fail("migration discovery", FileNotFoundError(", ".join(missing)))

    with conn.cursor() as cur:
        for path in migration_paths:
            sql = path.read_text(encoding="utf-8")
            cur.execute(sql)
    conn.commit()


def find_column(conn, table: str, column: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                  AND column_name = %s
            ) AS exists
            """,
            (table, column),
        )
        return bool(cur.fetchone()["exists"])


def run():
    print("[T22] Real PostgreSQL smoke test")
    conn = None
    test_user_id = None
    email = f"t22-smoke-{uuid4().hex}@example.invalid"

    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT current_database() AS db, version() AS version")
            row = cur.fetchone()
        print(f"[PASS] connection: {row['db']}")
        print(f"[INFO] postgres: {row['version'].splitlines()[0]}")

        apply_migrations(conn)
        print("[PASS] migrations: 001 + 002 applied")

        required_columns = [
            ("users", "email"),
            ("users", "password_hash"),
            ("user_sessions", "token_hash"),
            ("membership_grants", "user_id"),
            ("membership_grants", "product_id"),
        ]
        for table, column in required_columns:
            if not find_column(conn, table, column):
                fail("schema verification", RuntimeError(f"missing {table}.{column}"))
        print("[PASS] schema verification")

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users
                    (email, display_name, role, status, password_hash)
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING user_id
                """,
                (email, "T22 Smoke Test", "user", "active", "TEST_HASH_NOT_A_REAL_PASSWORD"),
            )
            test_user_id = cur.fetchone()["user_id"]

            cur.execute(
                """
                INSERT INTO user_sessions
                    (user_id, token_hash)
                VALUES
                    (%s, %s)
                RETURNING session_id
                """,
                (test_user_id, f"t22-token-hash-{uuid4().hex}"),
            )
            session_id = cur.fetchone()["session_id"]

            cur.execute(
                """
                INSERT INTO membership_grants
                    (user_id, product_id, status)
                VALUES
                    (%s, %s, %s)
                RETURNING grant_id
                """,
                (test_user_id, "action_plan_599", "active"),
            )
            grant_id = cur.fetchone()["grant_id"]

        conn.commit()
        print(f"[PASS] user/session/membership write: {test_user_id}")
        print(f"[INFO] session={session_id} grant={grant_id}")

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.email, g.product_id, g.status
                FROM users u
                JOIN membership_grants g ON g.user_id = u.user_id
                WHERE u.user_id = %s
                """,
                (test_user_id,),
            )
            access = cur.fetchone()

        if not access or access["status"] != "active":
            fail("entitlement read", RuntimeError("active membership grant not readable"))
        print(f"[PASS] entitlement read: {access['product_id']}")

        if not KEEP:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_sessions WHERE user_id = %s", (test_user_id,))
                cur.execute("DELETE FROM membership_grants WHERE user_id = %s", (test_user_id,))
                cur.execute("DELETE FROM users WHERE user_id = %s", (test_user_id,))
            conn.commit()
            print("[PASS] cleanup")
        else:
            print("[INFO] T22_KEEP_TEST_DATA=1, cleanup skipped")

        print("[PASS] T22 smoke test complete")
    except SystemExit:
        raise
    except Exception as exc:
        fail("runtime smoke test", exc)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    run()
