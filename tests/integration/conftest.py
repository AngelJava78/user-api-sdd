"""Fixtures de integración: PostgreSQL 17 real y efímero (testcontainers)."""

from collections.abc import Iterator

import pytest
from testcontainers.community.postgres import PostgresContainer


# TODO(T012): mover a tests/conftest.py junto con la app, el cliente httpx y el rollback por prueba.
@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer("postgres:17", driver="asyncpg") as postgres:
        yield postgres.get_connection_url()
