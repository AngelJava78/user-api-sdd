"""Creación de la aplicación FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import health, users
from app.config import Settings, get_settings
from app.infrastructure.database.engine import create_engine, create_sessionmaker
from app.infrastructure.logging import RequestIdMiddleware, configure_logging

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # La configuración se lee al arrancar, no al importar el módulo.
        app_settings = settings or get_settings()
        configure_logging(app_settings.log_level)
        engine = create_engine(app_settings)
        app.state.settings = app_settings
        app.state.sessionmaker = create_sessionmaker(engine)
        try:
            yield
        finally:
            await engine.dispose()

    # El contrato canónico es spec/openapi/users-api.yaml (Principio II): no se publica
    # el OpenAPI generado por el framework.
    app = FastAPI(
        title="Users API",
        lifespan=lifespan,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )
    register_error_handlers(app)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(users.router, prefix=API_PREFIX)
    return app


app = create_app()
