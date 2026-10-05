"""Configuración de Alembic (NFR-006). Upgrade/downgrade reales se prueban en T008."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from pydantic import ValidationError

from app.config import get_settings

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "src" / "app" / "infrastructure" / "database" / "migrations"
DATABASE_URL = "postgresql+asyncpg://user:s3cr3t@localhost:5432/users"


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Fuera de la raíz del repo para no leer un .env local.
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()


@pytest.fixture
def alembic_config() -> Config:
    return Config(toml_file=str(ROOT / "pyproject.toml"))


def test_script_location_points_to_migrations_package(alembic_config: Config) -> None:
    script = ScriptDirectory.from_config(alembic_config)

    assert Path(script.dir).resolve() == MIGRATIONS_DIR
    assert (MIGRATIONS_DIR / "env.py").is_file()


def test_offline_upgrade_uses_database_url_from_settings(
    alembic_config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    command.upgrade(alembic_config, "head", sql=True)


def test_env_requires_database_url(alembic_config: Config) -> None:
    with pytest.raises(ValidationError, match="database_url"):
        command.upgrade(alembic_config, "head", sql=True)
