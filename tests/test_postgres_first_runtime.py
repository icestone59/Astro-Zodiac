import os
import importlib


def test_memory_mode_rejected(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "memory")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    import runtime_config
    importlib.reload(runtime_config)
    try:
        runtime_config.validate_runtime_config()
    except RuntimeError as exc:
        assert "only runtime persistence backend" in str(exc)
    else:
        raise AssertionError("memory runtime must be rejected")


def test_missing_database_url_rejected(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "postgres")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import runtime_config
    importlib.reload(runtime_config)
    try:
        runtime_config.validate_runtime_config()
    except RuntimeError as exc:
        assert "DATABASE_URL" in str(exc)
    else:
        raise AssertionError("missing DATABASE_URL must be rejected")


def test_postgres_mode_accepted(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    import runtime_config
    importlib.reload(runtime_config)
    runtime_config.validate_runtime_config()
