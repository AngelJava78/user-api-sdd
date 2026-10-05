"""Entorno de Alembic (ADR-0005).

La URL de la base de datos llega de `Settings` (NFR-005), nunca de un archivo versionado.
Las migraciones se ejecutan como paso previo al despliegue, no al arrancar la API (ADR-0008).
"""

import asyncio
import logging
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.infrastructure.database.models import Base

config = context.config

# La CLI siempre pasa "alembic.ini" aunque no exista; sin él, logging mínimo
# para ver el progreso de las migraciones.
if config.config_file_name is not None and Path(config.config_file_name).is_file():
    fileConfig(config.config_file_name)
else:
    logging.basicConfig(format="%(levelname)-5.5s [%(name)s] %(message)s", level=logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la base (`alembic upgrade head --sql`)."""
    context.configure(
        url=get_settings().database_url.get_secret_value(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(
        get_settings().database_url.get_secret_value(),
        poolclass=pool.NullPool,
    )

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
