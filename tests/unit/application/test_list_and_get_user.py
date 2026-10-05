"""Casos de uso list_users y get_user con repositorio en memoria (FR-001, FR-002)."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.application.dto import UserPage
from app.application.use_cases.get_user import get_user
from app.application.use_cases.list_users import list_users
from app.domain.errors import UserNotFound
from app.domain.user import User
from app.domain.value_objects import Email, PersonName
from tests.unit.fakes import InMemoryUserRepository

START = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


def make_user(index: int, *, status: bool = True) -> User:
    user = User.create(
        email=Email.parse(f"user{index}@mail.com"),
        name=PersonName.parse("Ana", field="name"),
        lastname=PersonName.parse("López", field="lastname"),
        second_lastname=None,
        now=START + timedelta(minutes=index),
    )
    return replace(user, status=status)


@pytest.fixture
def repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


async def add_users(repository: InMemoryUserRepository, *users: User) -> None:
    for user in users:
        await repository.add(user)


async def test_list_users_returns_page_of_active_users(
    repository: InMemoryUserRepository,
) -> None:
    active = [make_user(i) for i in range(3)]
    await add_users(repository, *active, make_user(3, status=False))

    page = await list_users(limit=20, offset=0, repository=repository)

    assert page == UserPage(items=active, total=3, limit=20, offset=0)


async def test_list_users_applies_limit_and_offset(repository: InMemoryUserRepository) -> None:
    users = [make_user(i) for i in range(25)]
    await add_users(repository, *users)

    page = await list_users(limit=10, offset=20, repository=repository)

    assert page.items == users[20:25]
    assert (page.total, page.limit, page.offset) == (25, 10, 20)


async def test_list_users_offset_beyond_total_returns_empty_items(
    repository: InMemoryUserRepository,
) -> None:
    await add_users(repository, make_user(0))

    page = await list_users(limit=20, offset=5, repository=repository)

    assert page.items == []
    assert page.total == 1


async def test_get_user_returns_active_or_inactive_user(
    repository: InMemoryUserRepository,
) -> None:
    active, inactive = make_user(0), make_user(1, status=False)
    await add_users(repository, active, inactive)

    assert await get_user(active.id, repository) == active
    assert await get_user(inactive.id, repository) == inactive


async def test_get_user_raises_when_missing(repository: InMemoryUserRepository) -> None:
    missing = uuid4()

    with pytest.raises(UserNotFound) as error:
        await get_user(missing, repository)

    assert error.value.user_id == missing
