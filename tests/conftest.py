"""Fixtures compartidas: PostgreSQL 17 efímero, migraciones y sesión con rollback (R-09)."""

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from testcontainers.community.postgres import PostgresContainer

from app.api.dependencies import get_session
from app.config import Settings, get_settings
from app.infrastructure.database.engine import create_engine
from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """PostgreSQL vacío, uno por sesión de pruebas."""
    with PostgresContainer("postgres:17", driver="asyncpg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def migrated_database_url(database_url: str) -> str:
    """Aplica `alembic upgrade head` una vez por sesión."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", database_url)
        get_settings.cache_clear()
        command.upgrade(Config(toml_file=str(ROOT / "pyproject.toml")), "head")
    get_settings.cache_clear()
    return database_url


@pytest.fixture
def settings(migrated_database_url: str) -> Settings:
    return Settings(_env_file=None, database_url=migrated_database_url)


@pytest.fixture
async def engine(settings: Settings) -> AsyncIterator[AsyncEngine]:
    engine = create_engine(settings)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Sesión dentro de una transacción que se revierte al terminar la prueba.

    Los commit del código bajo prueba solo liberan savepoints; nada llega a confirmarse.
    """
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture
def app(settings: Settings, db_session: AsyncSession) -> FastAPI:
    """App con la sesión de cada petición sustituida por `db_session` (rollback)."""
    app = create_app(settings)

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    return app


@asynccontextmanager
async def running_client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """Arranca el lifespan de la app (httpx no lo hace) y devuelve un cliente sobre /api/v1."""
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
            yield client


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with running_client(app) as client:
        yield client
