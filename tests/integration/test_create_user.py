"""POST /users contra PostgreSQL real (US-1; FR-003, FR-004, FR-005, FR-006)."""

from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def payload(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {"email": "ana@mail.com", "name": "Ana", "lastname": "López"}
    body.update(overrides)
    return body


async def test_creates_active_user(client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    response = await client.post(
        "/users", json=payload(email="  Ana@Mail.com ", second_lastname="Pérez")
    )

    assert response.status_code == 201
    body = response.json()
    user_id = UUID(body["id"])
    assert body["email"] == "ana@mail.com"
    assert body["name"] == "Ana"
    assert body["lastname"] == "López"
    assert body["second_lastname"] == "Pérez"
    assert body["status"] is True
    created_at = datetime.fromisoformat(body["created_at"])
    assert created_at.tzinfo is not None
    assert body["updated_at"] == body["created_at"]
    assert response.headers["location"] == f"/api/v1/users/{user_id}"

    row = await db_session.execute(
        text("SELECT email, status FROM users WHERE id = :id"), {"id": user_id}
    )
    assert row.one() == ("ana@mail.com", True)


async def test_second_lastname_defaults_to_null(client: httpx.AsyncClient) -> None:
    response = await client.post("/users", json=payload())

    assert response.status_code == 201
    assert response.json()["second_lastname"] is None


async def test_rejects_duplicate_email_ignoring_case(client: httpx.AsyncClient) -> None:
    first = await client.post("/users", json=payload(email="Ana@Mail.com"))
    second = await client.post("/users", json=payload(email="ana@mail.com"))

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.parametrize(
    ("body", "field"),
    [
        (payload(name="x" * 31), "name"),
        (payload(lastname="L0pez"), "lastname"),
        (payload(second_lastname="-Pérez"), "second_lastname"),
        (payload(email="ana@mail"), "email"),
        ({"email": "ana@mail.com", "lastname": "López"}, "name"),
        (payload(status=False), "status"),
    ],
    ids=["name-31", "lastname-digit", "second_lastname-start", "email-format", "missing", "extra"],
)
async def test_rejects_invalid_payload(
    client: httpx.AsyncClient, body: dict[str, Any], field: str
) -> None:
    response = await client.post("/users", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert field in response.json()["details"]


async def test_rejects_missing_body(client: httpx.AsyncClient) -> None:
    response = await client.post("/users")

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
