import os

import pytest

from runtime_config import validate_runtime_config


def test_development_memory_allowed(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_ENV", "development")
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "memory")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    validate_runtime_config()


def test_production_memory_rejected(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_ENV", "production")
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "memory")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="requires ASTRO_ZODIAC_PERSISTENCE=postgres"):
        validate_runtime_config()


def test_postgres_without_database_url_rejected(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_ENV", "production")
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "postgres")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="requires DATABASE_URL"):
        validate_runtime_config()


def test_postgres_production_configuration_allowed(monkeypatch):
    monkeypatch.setenv("ASTRO_ZODIAC_ENV", "production")
    monkeypatch.setenv("ASTRO_ZODIAC_PERSISTENCE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    validate_runtime_config()
