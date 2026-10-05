"""Dos POST /users concurrentes con el mismo email → un 201 y un 409 (FR-004)."""

import asyncio
from collections.abc import AsyncIterator

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import Settings
from app.main import create_app
from tests.conftest import running_client

EMAIL_PREFIX = "concurrent-"
ROUNDS = 10


@pytest.fixture
async def committing_client(
    settings: Settings, engine: AsyncEngine
) -> AsyncIterator[httpx.AsyncClient]:
    """App con su propio pool: cada petición confirma en su propia conexión.

    El db_session con rollback comparte una sola conexión y no permite concurrencia real.
    """
    async with running_client(create_app(settings)) as client:
        yield client
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM users WHERE email LIKE :prefix"), {"prefix": f"{EMAIL_PREFIX}%"}
        )


async def test_concurrent_creations_with_same_email(
    committing_client: httpx.AsyncClient, engine: AsyncEngine
) -> None:
    for round_number in range(ROUNDS):
        email = f"{EMAIL_PREFIX}{round_number}@mail.com"
        body = {"email": email, "name": "Ana", "lastname": "López"}

        responses = await asyncio.gather(
            committing_client.post("/users", json=body),
            committing_client.post("/users", json={**body, "email": email.upper()}),
        )

        assert sorted(response.status_code for response in responses) == [201, 409], email
        conflict = next(response for response in responses if response.status_code == 409)
        assert conflict.json()["code"] == "EMAIL_ALREADY_EXISTS"
        async with engine.connect() as connection:
            count = await connection.execute(
                text("SELECT count(*) FROM users WHERE lower(email) = :email"), {"email": email}
            )
            assert count.scalar_one() == 1
