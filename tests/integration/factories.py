"""Inserción directa de usuarios para preparar escenarios de integración."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_CREATED_AT = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)

INSERT_USER = text(
    "INSERT INTO users (id, email, name, lastname, second_lastname, status, created_at,"
    " updated_at) VALUES (:id, :email, :name, :lastname, NULL, :status, :created_at,"
    " :created_at)"
)


async def insert_user(
    session: AsyncSession,
    *,
    email: str,
    status: bool = True,
    created_at: datetime = DEFAULT_CREATED_AT,
    user_id: UUID | None = None,
) -> UUID:
    user_id = user_id or uuid4()
    await session.execute(
        INSERT_USER,
        {
            "id": user_id,
            "email": email,
            "name": "Ana",
            "lastname": "López",
            "status": status,
            "created_at": created_at,
        },
    )
    return user_id


async def delete_all_users(session: AsyncSession) -> None:
    """Vacía la tabla dentro de la transacción de la prueba (se revierte al terminar)."""
    await session.execute(text("DELETE FROM users"))
