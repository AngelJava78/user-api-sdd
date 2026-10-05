"""Migraciones contra PostgreSQL real: upgrade sobre base vacía y downgrade completo (NFR-006)."""

import asyncio
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def alembic_config(
    database_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[Config]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    config = Config(toml_file=str(ROOT / "pyproject.toml"))
    # Cada prueba parte de una base vacía y la deja vacía.
    command.downgrade(config, "base")
    yield config
    command.downgrade(config, "base")
    get_settings.cache_clear()


def fetch(database_url: str, sql: str) -> list[tuple[Any, ...]]:
    async def run() -> list[tuple[Any, ...]]:
        engine = create_async_engine(database_url)
        try:
            async with engine.connect() as connection:
                result = await connection.execute(text(sql))
                return [tuple(row) for row in result]
        finally:
            await engine.dispose()

    return asyncio.run(run())


def users_table_exists(database_url: str) -> bool:
    return fetch(database_url, "SELECT to_regclass('public.users') IS NOT NULL")[0][0] is True


def current_revision(database_url: str) -> list[str]:
    return [row[0] for row in fetch(database_url, "SELECT version_num FROM alembic_version")]


def test_upgrade_on_empty_database_creates_schema(
    alembic_config: Config, database_url: str
) -> None:
    head = ScriptDirectory.from_config(alembic_config).get_current_head()
    assert not users_table_exists(database_url)

    command.upgrade(alembic_config, "head")

    assert current_revision(database_url) == [head]
    columns = fetch(
        database_url,
        """
        SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users'
        ORDER BY ordinal_position
        """,
    )
    assert columns == [
        ("id", "uuid", None, "NO", None),
        ("email", "character varying", 320, "NO", None),
        ("name", "character varying", 30, "NO", None),
        ("lastname", "character varying", 30, "NO", None),
        ("second_lastname", "character varying", 30, "YES", None),
        ("status", "boolean", None, "NO", "true"),
        ("created_at", "timestamp with time zone", None, "NO", None),
        ("updated_at", "timestamp with time zone", None, "NO", None),
    ]
    indexes = dict(
        fetch(database_url, "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users'")
    )
    assert indexes == {
        "pk_users": "CREATE UNIQUE INDEX pk_users ON public.users USING btree (id)",
        "ux_users_email_lower": (
            "CREATE UNIQUE INDEX ux_users_email_lower ON public.users "
            "USING btree (lower((email)::text))"
        ),
        "ix_users_status_created_at": (
            "CREATE INDEX ix_users_status_created_at ON public.users "
            "USING btree (status, created_at, id)"
        ),
    }


def test_full_downgrade_leaves_empty_database(alembic_config: Config, database_url: str) -> None:
    command.upgrade(alembic_config, "head")

    command.downgrade(alembic_config, "base")

    assert not users_table_exists(database_url)
    assert fetch(database_url, "SELECT count(*) FROM pg_indexes WHERE tablename = 'users'") == [
        (0,)
    ]
    assert current_revision(database_url) == []


def test_each_revision_upgrades_and_downgrades(alembic_config: Config, database_url: str) -> None:
    script = ScriptDirectory.from_config(alembic_config)
    revisions = list(reversed(list(script.walk_revisions("base", "heads"))))
    assert revisions, "no hay migraciones"

    for revision in revisions:
        command.upgrade(alembic_config, revision.revision)
        command.downgrade(alembic_config, revision.down_revision or "base")
        command.upgrade(alembic_config, revision.revision)
        assert current_revision(database_url) == [revision.revision]
