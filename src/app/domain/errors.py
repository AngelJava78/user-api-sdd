"""Errores de dominio. No dependen de HTTP ni de la base de datos (Principio IV)."""

from uuid import UUID


class DomainError(Exception):
    """Base de los errores de negocio."""


class UserNotFound(DomainError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User {user_id} not found")
        self.user_id = user_id


class EmailAlreadyExists(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__("Email already exists")
        self.email = email


class InvalidUserData(DomainError):
    def __init__(self, message: str, details: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
