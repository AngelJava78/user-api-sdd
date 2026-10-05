"""Caso de uso create_user con repositorio en memoria (FR-003, FR-004)."""

from datetime import UTC, datetime
from uuid import UUID

import pytest
from structlog.testing import capture_logs

from app.application.dto import CreateUserData
from app.application.use_cases.create_user import create_user
from app.domain.errors import EmailAlreadyExists, InvalidUserData
from tests.unit.fakes import InMemoryUserRepository

NOW = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


def clock() -> datetime:
    return NOW


@pytest.fixture
def repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


def data(email: str = "Ana@Mail.com", **overrides: str | None) -> CreateUserData:
    fields: dict[str, str | None] = {"name": "Ana", "lastname": "López", "second_lastname": None}
    fields.update(overrides)
    return CreateUserData(email=email, **fields)  # type: ignore[arg-type]


async def test_creates_active_user_with_generated_id(
    repository: InMemoryUserRepository,
) -> None:
    user = await create_user(data(email="  Ana@Mail.com "), repository, clock)

    assert isinstance(user.id, UUID)
    assert user.status is True
    assert user.email.value == "ana@mail.com"
    assert user.name.value == "Ana"
    assert user.lastname.value == "López"
    assert user.second_lastname is None
    assert user.created_at == user.updated_at == NOW
    assert repository.users == {user.id: user}


async def test_each_user_gets_a_distinct_id(repository: InMemoryUserRepository) -> None:
    first = await create_user(data(email="a@mail.com"), repository, clock)
    second = await create_user(data(email="b@mail.com"), repository, clock)

    assert first.id != second.id


async def test_rejects_duplicate_email_ignoring_case(repository: InMemoryUserRepository) -> None:
    existing = await create_user(data(email="Ana@Mail.com"), repository, clock)

    with pytest.raises(EmailAlreadyExists):
        await create_user(data(email="ana@mail.com"), repository, clock)

    assert list(repository.users) == [existing.id]


async def test_rejects_invalid_data_without_persisting(
    repository: InMemoryUserRepository,
) -> None:
    with pytest.raises(InvalidUserData) as error:
        await create_user(data(name="x" * 31), repository, clock)

    assert error.value.details is not None
    assert "name" in error.value.details
    assert repository.users == {}


async def test_blank_second_lastname_is_stored_as_none(
    repository: InMemoryUserRepository,
) -> None:
    user = await create_user(data(second_lastname="   "), repository, clock)

    assert user.second_lastname is None


async def test_keeps_valid_second_lastname(repository: InMemoryUserRepository) -> None:
    user = await create_user(data(second_lastname=" Pérez "), repository, clock)

    assert user.second_lastname is not None
    assert user.second_lastname.value == "Pérez"


async def test_logs_write_event(repository: InMemoryUserRepository) -> None:
    with capture_logs() as logs:
        user = await create_user(data(), repository, clock)

    assert {"event": "user_created", "user_id": str(user.id), "log_level": "info"} in logs
