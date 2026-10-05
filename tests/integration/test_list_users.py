"""GET /users contra PostgreSQL real (US-2; FR-001)."""

from datetime import timedelta
from uuid import UUID

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.factories import DEFAULT_CREATED_AT, delete_all_users, insert_user

USER_FIELDS = {
    "id",
    "email",
    "name",
    "lastname",
    "second_lastname",
    "status",
    "created_at",
    "updated_at",
}


@pytest.fixture(autouse=True)
async def empty_table(db_session: AsyncSession) -> None:
    # Otras pruebas (p. ej. contrato) pueden dejar usuarios confirmados en la base compartida.
    await delete_all_users(db_session)


async def insert_active(db_session: AsyncSession, count: int) -> list[UUID]:
    return [
        await insert_user(
            db_session,
            email=f"user{i}@mail.com",
            created_at=DEFAULT_CREATED_AT + timedelta(minutes=i),
        )
        for i in range(count)
    ]


def ids(body: dict[str, list[dict[str, str]]]) -> list[UUID]:
    return [UUID(item["id"]) for item in body["items"]]


async def test_lists_only_active_users(client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    active = await insert_active(db_session, 3)
    await insert_user(db_session, email="inactive@mail.com", status=False)

    response = await client.get("/users")

    assert response.status_code == 200
    body = response.json()
    assert ids(body) == active
    assert all(item["status"] is True for item in body["items"])
    assert (body["total"], body["limit"], body["offset"]) == (3, 20, 0)


async def test_items_match_user_schema(client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    await insert_active(db_session, 1)

    [item] = (await client.get("/users")).json()["items"]

    assert set(item) == USER_FIELDS


async def test_paginates_with_limit_and_offset(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    users = await insert_active(db_session, 25)

    body = (await client.get("/users", params={"limit": 10, "offset": 20})).json()

    assert ids(body) == users[20:25]
    assert (body["total"], body["limit"], body["offset"]) == (25, 10, 20)


async def test_default_limit_is_20(client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    await insert_active(db_session, 25)

    body = (await client.get("/users")).json()

    assert len(body["items"]) == 20
    assert (body["limit"], body["offset"]) == (20, 0)


async def test_order_is_stable_by_created_at_then_id(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    later = await insert_user(
        db_session, email="later@mail.com", created_at=DEFAULT_CREATED_AT + timedelta(hours=1)
    )
    # Mismo created_at: desempata el id.
    tied = sorted([await insert_user(db_session, email=f"tied{i}@mail.com") for i in range(3)])

    body = (await client.get("/users")).json()

    assert ids(body) == [*tied, later]


async def test_offset_beyond_total_returns_empty_items(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    await insert_active(db_session, 2)

    body = (await client.get("/users", params={"offset": 10})).json()

    assert body["items"] == []
    assert body["total"] == 2


async def test_huge_offset_returns_empty_items(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    # El contrato no acota offset; más allá de BIGINT sigue siendo "offset > total".
    await insert_active(db_session, 1)
    huge = 2**63

    response = await client.get("/users", params={"offset": huge})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 1, "limit": 20, "offset": huge}


async def test_empty_table(client: httpx.AsyncClient) -> None:
    body = (await client.get("/users")).json()

    assert body == {"items": [], "total": 0, "limit": 20, "offset": 0}


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"limit": 0}, "limit"),
        ({"limit": 101}, "limit"),
        ({"offset": -1}, "offset"),
        ({"limit": "abc"}, "limit"),
    ],
    ids=["limit-0", "limit-101", "offset-negative", "limit-not-int"],
)
async def test_rejects_out_of_range_pagination(
    client: httpx.AsyncClient, params: dict[str, object], field: str
) -> None:
    response = await client.get("/users", params=params)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert field in response.json()["details"]
