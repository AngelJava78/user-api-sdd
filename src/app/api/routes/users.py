"""Endpoints /users (spec/openapi/users-api.yaml)."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError

from app.api.dependencies import SessionDep, get_user_repository, reject_unknown_query_params
from app.api.schemas import CreateUserRequest, UserCollection, UserResponse
from app.application.dto import CreateUserData
from app.application.use_cases.create_user import create_user
from app.application.use_cases.get_user import get_user
from app.application.use_cases.list_users import list_users
from app.config import CONTRACT_MAX_LIMIT
from app.domain.repository import UserRepository

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(reject_unknown_query_params)],
)

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
    request: Request,
    limit: Annotated[int | None, Query(ge=1, le=CONTRACT_MAX_LIMIT)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    """Rango del contrato (1-100) más el límite configurado en Settings (ADR-0007)."""
    settings = request.app.state.settings
    if limit is None:
        limit = settings.pagination_default_limit
    elif limit > settings.pagination_max_limit:
        raise RequestValidationError(
            [
                {
                    "type": "less_than_equal",
                    "loc": ("query", "limit"),
                    "msg": f"Input should be less than or equal to {settings.pagination_max_limit}",
                    "input": limit,
                }
            ]
        )
    return Pagination(limit=limit, offset=offset)


@router.get("", response_model=UserCollection)
async def list_(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    repository: UserRepositoryDep,
) -> UserCollection:
    page = await list_users(limit=pagination.limit, offset=pagination.offset, repository=repository)
    return UserCollection.from_page(page)


@router.get("/{user_id}", response_model=UserResponse)
async def get(user_id: UUID, repository: UserRepositoryDep) -> UserResponse:
    return UserResponse.from_domain(await get_user(user_id, repository))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create(
    payload: CreateUserRequest,
    request: Request,
    response: Response,
    session: SessionDep,
    repository: UserRepositoryDep,
) -> UserResponse:
    user = await create_user(CreateUserData(**payload.model_dump()), repository, utc_now)
    await session.commit()
    response.headers["Location"] = f"{request.url.path}/{user.id}"
    return UserResponse.from_domain(user)
