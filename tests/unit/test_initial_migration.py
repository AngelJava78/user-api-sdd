"""Migración inicial de `users` en modo offline (FR-004, NFR-006).

Se valida el SQL generado sin base de datos; upgrade/downgrade reales se prueban en T008.
"""

import re
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from app.config import get_settings

ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = "postgresql+asyncpg://user:s3cr3t@localhost:5432/users"


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    get_settings.cache_clear()


@pytest.fixture
def alembic_config() -> Config:
    return Config(toml_file=str(ROOT / "pyproject.toml"))


def normalize(sql: str) -> str:
    return re.sub(r"\s+", " ", sql)


@pytest.fixture
def upgrade_sql(alembic_config: Config, capsys: pytest.CaptureFixture[str]) -> str:
    command.upgrade(alembic_config, "head", sql=True)
    return normalize(capsys.readouterr().out)


@pytest.fixture
def downgrade_sql(alembic_config: Config, capsys: pytest.CaptureFixture[str]) -> str:
    command.downgrade(alembic_config, "head:base", sql=True)
    return normalize(capsys.readouterr().out)


@pytest.mark.parametrize(
    "column",
    [
        "id UUID NOT NULL",
        "email VARCHAR(320) NOT NULL",
        "name VARCHAR(30) NOT NULL",
        "lastname VARCHAR(30) NOT NULL",
        "second_lastname VARCHAR(30),",
        "status BOOLEAN DEFAULT true NOT NULL",
        "created_at TIMESTAMP WITH TIME ZONE NOT NULL",
        "updated_at TIMESTAMP WITH TIME ZONE NOT NULL",
        "CONSTRAINT pk_users PRIMARY KEY (id)",
    ],
)
def test_upgrade_creates_users_table(upgrade_sql: str, column: str) -> None:
    assert "CREATE TABLE users (" in upgrade_sql
    assert column in upgrade_sql


def test_upgrade_creates_case_insensitive_unique_email_index(upgrade_sql: str) -> None:
    assert "CREATE UNIQUE INDEX ux_users_email_lower ON users (lower(email));" in upgrade_sql


def test_upgrade_creates_active_listing_index(upgrade_sql: str) -> None:
    assert (
        "CREATE INDEX ix_users_status_created_at ON users (status, created_at, id);" in upgrade_sql
    )


def test_downgrade_drops_everything(downgrade_sql: str) -> None:
    drop_listing = downgrade_sql.index("DROP INDEX ix_users_status_created_at;")
    drop_email = downgrade_sql.index("DROP INDEX ux_users_email_lower;")
    drop_table = downgrade_sql.index("DROP TABLE users;")

    assert max(drop_listing, drop_email) < drop_table
