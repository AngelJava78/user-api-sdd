"""Caso de uso: consultar un usuario por id, activo o inactivo (US-2; FR-002)."""

from uuid import UUID

from app.domain.errors import UserNotFound
from app.domain.repository import UserRepository
from app.domain.user import User


async def get_user(user_id: UUID, repository: UserRepository) -> User:
    user = await repository.get_by_id(user_id)
    if user is None:
        raise UserNotFound(user_id)
    return user
