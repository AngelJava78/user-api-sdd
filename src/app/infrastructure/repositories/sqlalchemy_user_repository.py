"""UserRepository sobre SQLAlchemy async y PostgreSQL (ADR-0005)."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.errors import EmailAlreadyExists
from app.domain.user import User
from app.domain.value_objects import Email, PersonName
from app.infrastructure.database.models import UserModel

EMAIL_UNIQUE_INDEX = "ux_users_email_lower"
# OFFSET de PostgreSQL es BIGINT; un offset mayor ya está, por definición, más allá del total.
PG_BIGINT_MAX = 2**63 - 1


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

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_domain(model) if model is not None else None

    async def list_active(self, limit: int, offset: int) -> list[User]:
        # Usa el índice ix_users_status_created_at (status, created_at, id).
        statement = (
            select(UserModel)
            .where(UserModel.status.is_(True))
            .order_by(UserModel.created_at, UserModel.id)
            .limit(limit)
            .offset(min(offset, PG_BIGINT_MAX))
        )
        models = await self._session.scalars(statement)
        return [_to_domain(model) for model in models]

    async def count_active(self) -> int:
        statement = select(func.count()).select_from(UserModel).where(UserModel.status.is_(True))
        return await self._session.scalar(statement) or 0


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


def _to_domain(model: UserModel) -> User:
    # Los datos persistidos ya pasaron la validación de dominio al crearse.
    return User(
        id=model.id,
        email=Email(model.email),
        name=PersonName(model.name),
        lastname=PersonName(model.lastname),
        second_lastname=PersonName(model.second_lastname) if model.second_lastname else None,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
