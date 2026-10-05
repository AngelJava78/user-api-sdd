"""Dependencias de FastAPI: recursos por petición."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.dependencies.models import Dependant
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repository import UserRepository
from app.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.sessionmaker
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def reject_unknown_query_params(request: Request) -> None:
    """Rechaza los parámetros de consulta que la ruta no declara (spec/acceptance.md).

    Misma regla que additionalProperties: false en los cuerpos: lo que no está en el
    contrato se rechaza con 422 VALIDATION_ERROR.
    """
    route = request.scope.get("route")
    if not isinstance(route, APIRoute):
        return
    declared = _declared_query_params(route.dependant)
    unknown = [name for name in request.query_params if name not in declared]
    if unknown:
        raise RequestValidationError(
            [
                {
                    "type": "extra_forbidden",
                    "loc": ("query", name),
                    "msg": "Unknown query parameter",
                    "input": request.query_params[name],
                }
                for name in unknown
            ]
        )


def _declared_query_params(dependant: Dependant) -> set[str]:
    """Parámetros de consulta de la ruta y de sus dependencias (p. ej. la paginación)."""
    names = {param.alias for param in dependant.query_params}
    for sub_dependant in dependant.dependencies:
        names |= _declared_query_params(sub_dependant)
    return names
