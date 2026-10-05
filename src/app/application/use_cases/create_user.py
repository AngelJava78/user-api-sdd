"""Caso de uso: registrar un usuario (US-1; FR-003, FR-004, FR-005, FR-006)."""

from collections.abc import Callable
from datetime import datetime

import structlog

from app.application.dto import CreateUserData
from app.domain.errors import InvalidUserData
from app.domain.repository import UserRepository
from app.domain.user import User
from app.domain.value_objects import Email, PersonName

logger = structlog.get_logger(__name__)


async def create_user(
    data: CreateUserData, repository: UserRepository, clock: Callable[[], datetime]
) -> User:
    """Crea un usuario activo.

    La unicidad del email no se comprueba aquí: una consulta previa tendría una condición
    de carrera. La garantiza el repositorio (índice único en PostgreSQL), que lanza
    EmailAlreadyExists.
    """
    details: dict[str, str] = {}

    def collect[T](parse: Callable[[], T]) -> T | None:
        try:
            return parse()
        except InvalidUserData as error:
            details.update(error.details or {})
            return None

    email = collect(lambda: Email.parse(data.email))
    name = collect(lambda: PersonName.parse(data.name, field="name"))
    lastname = collect(lambda: PersonName.parse(data.lastname, field="lastname"))
    second_lastname = collect(
        lambda: PersonName.parse_optional(data.second_lastname, field="second_lastname")
    )
    if details or email is None or name is None or lastname is None:
        raise InvalidUserData("Invalid user data", details=details)

    user = User.create(
        email=email,
        name=name,
        lastname=lastname,
        second_lastname=second_lastname,
        now=clock(),
    )
    await repository.add(user)
    logger.info("user_created", user_id=str(user.id))
    return user
