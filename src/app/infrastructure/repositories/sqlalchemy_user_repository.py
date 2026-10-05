"""UserRepository sobre SQLAlchemy async y PostgreSQL (ADR-0005)."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.errors import EmailAlreadyExists
from app.domain.user import User
from app.infrastructure.database.models import UserModel

EMAIL_UNIQUE_INDEX = "ux_users_email_lower"


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(_to_model(user))
        try:
            # flush ejecuta el INSERT: el índice único resuelve también la concurrencia (FR-004).
            await self._session.flush()
        except IntegrityError as error:
            await self._session.rollback()
            if _violated_constraint(error) == EMAIL_UNIQUE_INDEX:
                raise EmailAlreadyExists(user.email.value) from error
            raise


def _violated_constraint(error: IntegrityError) -> str | None:
    # asyncpg expone el nombre de la restricción en la excepción original.
    cause = error.orig.__cause__ if error.orig is not None else None
    constraint = getattr(cause, "constraint_name", None)
    return constraint if isinstance(constraint, str) else None


def _to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=user.email.value,
        name=user.name.value,
        lastname=user.lastname.value,
        second_lastname=user.second_lastname.value if user.second_lastname else None,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
