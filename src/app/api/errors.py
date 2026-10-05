"""Traducción de errores a respuestas HTTP con el esquema `Error` (FR-010)."""

from collections.abc import Mapping

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.schemas import ErrorCode, ErrorResponse
from app.domain.errors import EmailAlreadyExists, InvalidUserData, UserNotFound

logger = structlog.get_logger(__name__)

# Errores del framework (rutas o métodos fuera del contrato).
_HTTP_STATUS_CODES = {
    status.HTTP_404_NOT_FOUND: ErrorCode.NOT_FOUND,
    status.HTTP_405_METHOD_NOT_ALLOWED: ErrorCode.METHOD_NOT_ALLOWED,
}


def error_response(
    status_code: int,
    code: ErrorCode,
    message: str,
    details: dict[str, str] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body = ErrorResponse(code=code, message=message, details=details)
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json", exclude_none=True),
        headers=headers,
    )


def _field_name(loc: tuple[int | str, ...]) -> str:
    # ("body", "name") → "name"; ("body",) → "body"
    return str(loc[-1]) if len(loc) > 1 else str(loc[0])


async def _handle_request_validation(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    details: dict[str, str] = {}
    for error in exc.errors():
        details.setdefault(_field_name(tuple(error["loc"])), error["msg"])
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        ErrorCode.VALIDATION_ERROR,
        "Request validation failed",
        details,
    )


async def _handle_invalid_user_data(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, InvalidUserData)
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        ErrorCode.VALIDATION_ERROR,
        exc.message,
        exc.details,
    )


async def _handle_user_not_found(request: Request, exc: Exception) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, ErrorCode.USER_NOT_FOUND, "User not found")


async def _handle_email_already_exists(request: Request, exc: Exception) -> JSONResponse:
    return error_response(
        status.HTTP_409_CONFLICT, ErrorCode.EMAIL_ALREADY_EXISTS, "Email already exists"
    )


async def _handle_http_exception(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    default = (
        ErrorCode.INTERNAL_ERROR
        if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR
        else ErrorCode.VALIDATION_ERROR
    )
    # El contrato no documenta 400: un cuerpo ilegible se trata como error de validación (422).
    status_code = (
        status.HTTP_422_UNPROCESSABLE_CONTENT
        if exc.status_code == status.HTTP_400_BAD_REQUEST
        else exc.status_code
    )
    return error_response(
        status_code,
        _HTTP_STATUS_CODES.get(exc.status_code, default),
        str(exc.detail),
        headers=exc.headers,  # conserva, p. ej., Allow en 405
    )


async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception")
    # Mensaje genérico: no se exponen detalles internos al cliente.
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCode.INTERNAL_ERROR, "Internal server error"
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _handle_request_validation)
    app.add_exception_handler(InvalidUserData, _handle_invalid_user_data)
    app.add_exception_handler(UserNotFound, _handle_user_not_found)
    app.add_exception_handler(EmailAlreadyExists, _handle_email_already_exists)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(Exception, _handle_unexpected)
