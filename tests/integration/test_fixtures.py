"""Autoprueba de las fixtures de tests/conftest.py (T012)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

INSERT_USER = text(
    "INSERT INTO users (id, email, name, lastname, created_at, updated_at) "
    "VALUES (gen_random_uuid(), :email, 'Ana', 'López', now(), now())"
)
COUNT_BY_EMAIL = text("SELECT count(*) FROM users WHERE email = :email")


async def test_database_is_migrated(db_session: AsyncSession) -> None:
    result = await db_session.execute(text("SELECT to_regclass('public.users') IS NOT NULL"))
    assert result.scalar_one() is True


async def test_commits_stay_inside_test_transaction(
    db_session: AsyncSession, engine: AsyncEngine
) -> None:
    await db_session.execute(INSERT_USER, {"email": "rollback@mail.com"})
    await db_session.commit()  # el código de la app puede hacer commit

    count = await db_session.execute(COUNT_BY_EMAIL, {"email": "rollback@mail.com"})
    assert count.scalar_one() == 1

    # Otra conexión no ve la fila: la transacción externa nunca se confirma.
    async with engine.connect() as other:
        count = await other.execute(COUNT_BY_EMAIL, {"email": "rollback@mail.com"})
        assert count.scalar_one() == 0
