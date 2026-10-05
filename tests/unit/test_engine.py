"""Engine async, sessionmaker y pool configurable (ADR-0005). Sin base de datos."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.infrastructure.database.engine import create_engine, create_sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:s3cr3t@localhost:5432/users"


def make_settings(**overrides: Any) -> Settings:
    return Settings(_env_file=None, database_url=DATABASE_URL, **overrides)


def test_pool_uses_adr_defaults() -> None:
    engine = create_engine(make_settings())
    pool: Any = engine.pool

    assert pool.size() == 10
    assert pool._max_overflow == 5
    assert pool._timeout == 5
    assert pool._pre_ping is True


def test_pool_is_configurable_by_settings() -> None:
    engine = create_engine(
        make_settings(db_pool_size=3, db_max_overflow=0, db_pool_timeout_seconds=1.5)
    )
    pool: Any = engine.pool

    assert pool.size() == 3
    assert pool._max_overflow == 0
    assert pool._timeout == 1.5


def test_engine_uses_asyncpg_and_hides_password() -> None:
    engine = create_engine(make_settings())

    assert engine.dialect.driver == "asyncpg"
    assert engine.url.database == "users"
    assert "s3cr3t" not in repr(engine)
    assert "s3cr3t" not in str(engine.url)


def test_sessionmaker_binds_engine_without_expiring_on_commit() -> None:
    engine = create_engine(make_settings())
    session_factory = create_sessionmaker(engine)

    session = session_factory()

    assert isinstance(session, AsyncSession)
    assert session.bind is engine
    assert session.sync_session.expire_on_commit is False
