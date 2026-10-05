"""Modelos de request/response: espejo de spec/openapi/users-api.yaml."""

from enum import StrEnum

from pydantic import BaseModel


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
