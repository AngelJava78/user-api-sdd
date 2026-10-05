"""Puerto de persistencia de usuarios (ADR-0001: las dependencias apuntan al dominio)."""

from typing import Protocol
from uuid import UUID

from app.domain.user import User


class UserRepository(Protocol):
    async def add(self, user: User) -> None:
        """Persiste un usuario nuevo.

        Raises:
            EmailAlreadyExists: si el email ya está registrado (sin distinguir mayúsculas).
        """
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Devuelve el usuario, activo o inactivo, o None si no existe."""
        ...

    async def list_active(self, limit: int, offset: int) -> list[User]:
        """Página de usuarios activos en orden estable `created_at, id`."""
        ...

    async def count_active(self) -> int: ...
