"""GET /health/live y GET /health/ready (FR-011, NFR-008)."""

import httpx

from app.config import Settings
from app.main import create_app
from tests.conftest import running_client

UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://user:pass@127.0.0.1:1/users"


async def test_live_returns_ok(client: httpx.AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_returns_ok_when_database_responds(client: httpx.AsyncClient) -> None:
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_returns_503_when_database_is_unreachable() -> None:
    settings = Settings(_env_file=None, database_url=UNREACHABLE_DATABASE_URL)

    async with running_client(create_app(settings)) as client:
        ready = await client.get("/health/ready")
        live = await client.get("/health/live")

    assert ready.status_code == 503
    assert ready.json()["code"] == "SERVICE_UNAVAILABLE"
    # live no consulta la base: el proceso sigue vivo.
    assert live.status_code == 200


async def test_generated_openapi_and_docs_are_exposed(client: httpx.AsyncClient) -> None:
    # Documentación derivada del código. La fuente de verdad sigue siendo
    # spec/openapi/users-api.yaml, validado con Schemathesis (Principio II).
    openapi = await client.get("http://test/openapi.json")
    assert openapi.status_code == 200
    assert {"/api/v1/users", "/api/v1/users/{user_id}", "/api/v1/health/ready"} <= set(
        openapi.json()["paths"]
    )

    for path in ("http://test/docs", "http://test/redoc"):
        response = await client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
