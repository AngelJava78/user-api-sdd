"""Puerto de persistencia de usuarios (ADR-0001: las dependencias apuntan al dominio)."""

from typing import Protocol

from app.domain.user import User


class UserRepository(Protocol):
    async def add(self, user: User) -> None:
        """Persiste un usuario nuevo.

        Raises:
            EmailAlreadyExists: si el email ya está registrado (sin distinguir mayúsculas).
        """
        ...
