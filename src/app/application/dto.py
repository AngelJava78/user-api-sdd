"""Datos de entrada de los casos de uso."""

from dataclasses import dataclass

from app.domain.user import User


@dataclass(frozen=True, kw_only=True)
class CreateUserData:
    email: str
    name: str
    lastname: str
    second_lastname: str | None = None


@dataclass(frozen=True, kw_only=True)
class UserPage:
    items: list[User]
    total: int
    limit: int
    offset: int
