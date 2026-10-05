"""GET /users/{user_id} contra PostgreSQL real (US-2; FR-002)."""

from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.factories import insert_user


async def test_returns_user_created_with_post(client: httpx.AsyncClient) -> None:
    created = await client.post(
        "/users", json={"email": "ana@mail.com", "name": "Ana", "lastname": "López"}
    )

    response = await client.get(f"/users/{created.json()['id']}")

    assert response.status_code == 200
    assert response.json() == created.json()


async def test_returns_inactive_user(client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    user_id = await insert_user(db_session, email="inactive@mail.com", status=False)

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(user_id)
    assert response.json()["status"] is False


async def test_unknown_id_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get(f"/users/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["code"] == "USER_NOT_FOUND"


async def test_non_uuid_id_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.get("/users/abc")

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "user_id" in response.json()["details"]
