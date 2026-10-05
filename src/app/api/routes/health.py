"""Sondas de salud para el orquestador y el balanceador (FR-011, ADR-0008)."""

import asyncio
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.api.errors import error_response
from app.api.schemas import ErrorCode, Health

router = APIRouter(prefix="/health", tags=["Health"])
logger = structlog.get_logger(__name__)


@router.get("/live", response_model=Health)
async def live() -> Health:
    # No consulta dependencias: si falla, el orquestador reinicia la instancia.
    return Health(status="ok")


@router.get("/ready", response_model=Health)
async def ready(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> Health | JSONResponse:
    timeout = request.app.state.settings.readiness_db_timeout_seconds
    try:
        await asyncio.wait_for(session.execute(text("SELECT 1")), timeout)
    except (TimeoutError, OSError, SQLAlchemyError) as exc:
        logger.warning("readiness_check_failed", error=type(exc).__name__)
        return error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Database unavailable",
        )
    return Health(status="ok")
