"""Datos de entrada de los casos de uso."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CreateUserData:
    email: str
    name: str
    lastname: str
    second_lastname: str | None = None
