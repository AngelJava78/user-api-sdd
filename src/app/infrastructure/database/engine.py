"""Engine async y fábrica de sesiones de SQLAlchemy (ADR-0005)."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url.get_secret_value(),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        # Falla rápido en lugar de encolar indefinidamente cuando el pool se agota.
        pool_timeout=settings.db_pool_timeout_seconds,
        pool_pre_ping=True,
    )


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False evita cargas perezosas implícitas tras el commit,
    # que en modo async fallarían fuera de un contexto await.
    return async_sessionmaker(engine, expire_on_commit=False)
