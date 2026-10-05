"""Manejadores HTTP que devuelven el esquema `Error` del contrato (FR-010)."""

from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

import httpx
import pytest
from fastapi import FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field

from app.api.errors import register_error_handlers
from app.domain.errors import EmailAlreadyExists, InvalidUserData, UserNotFound

USER_ID = UUID("8d5f6f2e-0a51-4f3e-9b8e-1c2d3e4f5a6b")


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(max_length=30)


def build_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/not-found")
    async def not_found() -> None:
        raise UserNotFound(USER_ID)

    @app.get("/duplicated")
    async def duplicated() -> None:
        raise EmailAlreadyExists("ana@mail.com")

    @app.get("/invalid")
    async def invalid() -> None:
        raise InvalidUserData("Datos de usuario no válidos", details={"name": "inválido"})

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secreto interno")

    @app.post("/validate/{user_id}")
    async def validate(user_id: UUID, payload: Payload, limit: int = Query(le=100)) -> None:
        return None

    return app


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=build_app(), raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def assert_error(response: httpx.Response, status: int, code: str) -> dict[str, Any]:
    assert response.status_code == status
    assert response.headers["content-type"] == "application/json"
    body: dict[str, Any] = response.json()
    assert body["code"] == code
    assert isinstance(body["message"], str)
    assert body["message"]
    assert set(body) <= {"code", "message", "details"}
    return body


async def test_user_not_found_returns_404(client: httpx.AsyncClient) -> None:
    body = assert_error(await client.get("/not-found"), 404, "USER_NOT_FOUND")
    assert "details" not in body


async def test_email_already_exists_returns_409(client: httpx.AsyncClient) -> None:
    assert_error(await client.get("/duplicated"), 409, "EMAIL_ALREADY_EXISTS")


async def test_invalid_user_data_returns_422_with_details(client: httpx.AsyncClient) -> None:
    body = assert_error(await client.get("/invalid"), 422, "VALIDATION_ERROR")
    assert body["details"] == {"name": "inválido"}


async def test_request_validation_returns_422_with_field_details(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/validate/no-es-uuid",
        params={"limit": 101},
        json={"name": "x" * 31, "email": "a@b.com"},
    )

    body = assert_error(response, 422, "VALIDATION_ERROR")
    assert set(body["details"]) == {"user_id", "limit", "name", "email"}
    assert all(isinstance(message, str) for message in body["details"].values())


async def test_missing_body_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.post(f"/validate/{USER_ID}", params={"limit": 1})

    body = assert_error(response, 422, "VALIDATION_ERROR")
    assert "body" in body["details"]


async def test_unhandled_exception_returns_500_without_leaking(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/boom")

    assert_error(response, 500, "INTERNAL_ERROR")
    assert "secreto" not in response.text


async def test_unknown_route_returns_not_found(client: httpx.AsyncClient) -> None:
    assert_error(await client.get("/no-existe"), 404, "NOT_FOUND")


async def test_unsupported_method_returns_method_not_allowed(
    client: httpx.AsyncClient,
) -> None:
    assert_error(await client.delete("/not-found"), 405, "METHOD_NOT_ALLOWED")


def test_domain_errors_carry_context() -> None:
    assert UserNotFound(USER_ID).user_id == USER_ID
    assert EmailAlreadyExists("ana@mail.com").email == "ana@mail.com"
    assert InvalidUserData("x").details is None
