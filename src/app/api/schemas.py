"""Modelos de request/response: espejo de spec/openapi/users-api.yaml."""

from datetime import datetime
from enum import StrEnum
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.application.dto import UserPage
from app.domain.user import User


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, str] | None = None


class Health(BaseModel):
    status: Literal["ok"]


class CreateUserRequest(BaseModel):
    """CreateUser del contrato; las reglas de dominio se validan en los value objects."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=320)
    name: str = Field(min_length=1, max_length=30)
    lastname: str = Field(min_length=1, max_length=30)
    second_lastname: str | None = Field(default=None, min_length=1, max_length=30)


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    lastname: str
    second_lastname: str | None
    status: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> Self:
        return cls(
            id=user.id,
            email=user.email.value,
            name=user.name.value,
            lastname=user.lastname.value,
            second_lastname=user.second_lastname.value if user.second_lastname else None,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserCollection(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_page(cls, page: UserPage) -> Self:
        return cls(
            items=[UserResponse.from_domain(user) for user in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
