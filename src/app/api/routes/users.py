"""Endpoints /users (spec/openapi/users-api.yaml)."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import SessionDep, get_user_repository
from app.api.schemas import CreateUserRequest, UserResponse
from app.application.dto import CreateUserData
from app.application.use_cases.create_user import create_user
from app.domain.repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def utc_now() -> datetime:
    return datetime.now(UTC)


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
