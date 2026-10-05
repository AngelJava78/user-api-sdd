"""Logs JSON con request_id, método, ruta, código y duración (NFR-004)."""

import json
import logging
from collections.abc import AsyncIterator, Iterator
from typing import Any
from uuid import UUID

import httpx
import pytest
import structlog
from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.infrastructure.logging import RequestIdMiddleware, configure_logging


@pytest.fixture(autouse=True)
def restore_logging() -> Iterator[None]:
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers, root.level = handlers, level
    structlog.reset_defaults()


def build_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)
    app.add_middleware(RequestIdMiddleware)
    logger = structlog.get_logger("test")

    @app.get("/ok")
    async def ok() -> dict[str, str]:
        logger.info("inside_handler")
        return {"status": "ok"}

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    return app


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=build_app(), raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def read_logs(capsys: pytest.CaptureFixture[str]) -> list[dict[str, Any]]:
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]  # falla si alguna línea no es JSON


def by_event(logs: list[dict[str, Any]], event: str) -> list[dict[str, Any]]:
    return [log for log in logs if log["event"] == event]


async def test_each_request_emits_one_json_line_with_required_fields(
    client: httpx.AsyncClient, capsys: pytest.CaptureFixture[str]
) -> None:
    configure_logging("INFO")

    await client.get("/ok?secret=1")

    [entry] = by_event(read_logs(capsys), "http_request")
    UUID(entry["request_id"])
    assert entry["method"] == "GET"
    assert entry["path"] == "/ok"
    assert entry["status_code"] == 200
    assert isinstance(entry["duration_ms"], float)
    assert entry["duration_ms"] >= 0
    assert entry["level"] == "info"
    assert entry["timestamp"].endswith("Z")


async def test_logs_inside_request_share_request_id(
    client: httpx.AsyncClient, capsys: pytest.CaptureFixture[str]
) -> None:
    configure_logging("INFO")

    await client.get("/ok")
    await client.get("/ok")

    logs = read_logs(capsys)
    inner = [log["request_id"] for log in by_event(logs, "inside_handler")]
    outer = [log["request_id"] for log in by_event(logs, "http_request")]
    assert inner == outer
    assert len(set(outer)) == 2


async def test_unhandled_exception_is_logged_with_status_500(
    client: httpx.AsyncClient, capsys: pytest.CaptureFixture[str]
) -> None:
    configure_logging("INFO")

    await client.get("/boom")

    logs = read_logs(capsys)
    [request] = by_event(logs, "http_request")
    [error] = by_event(logs, "unhandled_exception")
    assert request["status_code"] == 500
    assert error["level"] == "error"
    assert error["request_id"] == request["request_id"]
    assert "RuntimeError" in error["exception"]


def test_stdlib_loggers_are_rendered_as_json(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")

    logging.getLogger("uvicorn.error").info("server started")

    [entry] = read_logs(capsys)
    assert entry["event"] == "server started"
    assert entry["level"] == "info"


def test_log_level_filters_lower_levels(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("WARNING")

    structlog.get_logger("test").info("hidden")
    structlog.get_logger("test").warning("visible")

    assert [log["event"] for log in read_logs(capsys)] == ["visible"]
