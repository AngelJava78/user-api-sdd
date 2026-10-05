"""Engine y sesión contra PostgreSQL real (ADR-0005)."""

import time

import pytest
from sqlalchemy import exc, text

from app.config import Settings
from app.infrastructure.database.engine import create_engine, create_sessionmaker


async def test_session_executes_queries(database_url: str) -> None:
    engine = create_engine(Settings(_env_file=None, database_url=database_url))
    try:
        async with create_sessionmaker(engine)() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
    finally:
        await engine.dispose()


async def test_exhausted_pool_fails_fast(database_url: str) -> None:
    settings = Settings(
        _env_file=None,
        database_url=database_url,
        db_pool_size=1,
        db_max_overflow=0,
        db_pool_timeout_seconds=0.5,
    )
    engine = create_engine(settings)
    try:
        async with engine.connect():
            started = time.monotonic()
            with pytest.raises(exc.TimeoutError):
                async with engine.connect():
                    pass
            assert time.monotonic() - started < 2
    finally:
        await engine.dispose()
