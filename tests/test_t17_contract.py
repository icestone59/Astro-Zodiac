from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]


def test_sql_has_core_tables_and_no_destructive_commands():
    sql = (ROOT / "migrations" / "001_initial_postgres.sql").read_text()
    for table in [
        "users", "user_profiles", "membership_grants", "orders", "payments",
        "webhook_events", "charts", "analyses", "validation_sessions",
        "action_plans", "daily_checkins", "weekly_reviews", "plan_adjustments",
        "ai_usage_events",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql
    assert not re.search(r"\bDROP\s+(TABLE|SCHEMA|DATABASE)\b", sql, re.I)


def test_python_modules_compile():
    for name in ["postgres_connection.py", "postgres_repository.py"]:
        ast.parse((ROOT / name).read_text())


def test_repository_uses_parameterized_sql():
    text = (ROOT / "postgres_repository.py").read_text()
    assert "%s" in text
    assert "f\"" not in text
    assert "format(" not in text
