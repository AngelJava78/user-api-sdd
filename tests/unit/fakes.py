"""Dobles de prueba para la capa de aplicación."""

from uuid import UUID

from app.domain.errors import EmailAlreadyExists
from app.domain.user import User


class InMemoryUserRepository:
    """Implementación en memoria de UserRepository.

    Reproduce la unicidad case-insensitive del índice ux_users_email_lower (FR-004).
    """

    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        if any(stored.email == user.email for stored in self.users.values()):
            raise EmailAlreadyExists(user.email.value)
        self.users[user.id] = user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def list_active(self, limit: int, offset: int) -> list[User]:
        active = sorted(
            (user for user in self.users.values() if user.status),
            key=lambda user: (user.created_at, user.id),
        )
        return active[offset : offset + limit]

    async def count_active(self) -> int:
        return sum(1 for user in self.users.values() if user.status)
