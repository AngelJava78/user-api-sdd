"""Paginación configurable por Settings dentro del rango del contrato (ADR-0007, T004)."""

from collections.abc import AsyncIterator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.config import Settings
from app.main import create_app
from tests.conftest import running_client


@pytest.fixture
async def client_with_limits(
    migrated_database_url: str, db_session: AsyncSession
) -> AsyncIterator[httpx.AsyncClient]:
    settings = Settings(
        _env_file=None,
        database_url=migrated_database_url,
        pagination_default_limit=5,
        pagination_max_limit=50,
    )
    app = create_app(settings)

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with running_client(app) as client:
        yield client


async def test_uses_configured_default_limit(client_with_limits: httpx.AsyncClient) -> None:
    body = (await client_with_limits.get("/users")).json()

    assert body["limit"] == 5


async def test_accepts_configured_max_limit(client_with_limits: httpx.AsyncClient) -> None:
    response = await client_with_limits.get("/users", params={"limit": 50})

    assert response.status_code == 200


async def test_rejects_limit_above_configured_max(client_with_limits: httpx.AsyncClient) -> None:
    response = await client_with_limits.get("/users", params={"limit": 51})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "limit" in response.json()["details"]
