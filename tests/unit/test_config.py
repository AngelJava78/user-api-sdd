"""Pruebas de `Settings` (NFR-005: configuración por variables de entorno)."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings

DATABASE_URL = "postgresql+asyncpg://user:s3cr3t@localhost:5432/users"

SETTINGS_ENV_VARS = (
    "APP_ENV",
    "APP_NAME",
    "LOG_LEVEL",
    "DATABASE_URL",
    "DB_POOL_SIZE",
    "DB_MAX_OVERFLOW",
    "DB_POOL_TIMEOUT_SECONDS",
    "PAGINATION_DEFAULT_LIMIT",
    "PAGINATION_MAX_LIMIT",
    "SHUTDOWN_GRACE_SECONDS",
    "READINESS_DB_TIMEOUT_SECONDS",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in SETTINGS_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()


def make_settings() -> Settings:
    # _env_file=None aísla la prueba de un .env local.
    return Settings(_env_file=None)


def test_defaults_match_env_example(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    settings = make_settings()

    assert settings.app_env == "development"
    assert settings.app_name == "users-api"
    assert settings.log_level == "INFO"
    assert settings.db_pool_size == 10
    assert settings.db_max_overflow == 5
    assert settings.db_pool_timeout_seconds == 5
    assert settings.pagination_default_limit == 20
    assert settings.pagination_max_limit == 100
    assert settings.shutdown_grace_seconds == 30
    assert settings.readiness_db_timeout_seconds == 2


def test_environment_variables_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("DB_POOL_SIZE", "20")
    monkeypatch.setenv("PAGINATION_MAX_LIMIT", "50")

    settings = make_settings()

    assert settings.app_env == "production"
    assert settings.log_level == "WARNING"
    assert settings.db_pool_size == 20
    assert settings.pagination_max_limit == 50
    assert settings.database_url.get_secret_value() == DATABASE_URL


def test_reads_env_file_and_ignores_unrelated_keys(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"DATABASE_URL={DATABASE_URL}\n"
        "DB_POOL_SIZE=7\n"
        "POSTGRES_USER=user\n"
        "POSTGRES_PASSWORD=s3cr3t\n"
        "WEB_CONCURRENCY=2   # workers por réplica\n",
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.db_pool_size == 7
    assert settings.database_url.get_secret_value() == DATABASE_URL


def test_database_url_is_required() -> None:
    with pytest.raises(ValidationError, match="database_url"):
        make_settings()


def test_database_url_is_not_exposed_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    settings = make_settings()

    assert "s3cr3t" not in repr(settings)
    assert "s3cr3t" not in str(settings.model_dump())


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("LOG_LEVEL", "FOO"),
        ("DB_POOL_SIZE", "0"),
        ("DB_MAX_OVERFLOW", "-1"),
        ("DB_POOL_TIMEOUT_SECONDS", "0"),
        ("SHUTDOWN_GRACE_SECONDS", "-1"),
        ("READINESS_DB_TIMEOUT_SECONDS", "0"),
        ("PAGINATION_DEFAULT_LIMIT", "0"),
        ("PAGINATION_MAX_LIMIT", "0"),
    ],
)
def test_rejects_out_of_range_values(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv(name, value)

    with pytest.raises(ValidationError):
        make_settings()


@pytest.mark.parametrize(
    ("default_limit", "max_limit"),
    [
        ("20", "101"),  # el contrato OpenAPI fija limit <= 100
        ("30", "25"),  # el valor por defecto no puede superar el máximo
    ],
)
def test_pagination_must_stay_within_contract(
    monkeypatch: pytest.MonkeyPatch, default_limit: str, max_limit: str
) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("PAGINATION_DEFAULT_LIMIT", default_limit)
    monkeypatch.setenv("PAGINATION_MAX_LIMIT", max_limit)

    with pytest.raises(ValidationError):
        make_settings()


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    assert get_settings() is get_settings()
