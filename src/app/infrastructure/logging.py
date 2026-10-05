"""Logs JSON estructurados con `request_id` por petición (NFR-004, Principio VIII)."""

import logging
import sys
import time
from uuid import uuid4

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)

_SHARED_PROCESSORS: list[structlog.typing.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
]


class _StdoutHandler(logging.StreamHandler):  # type: ignore[type-arg]
    """Escribe en el `sys.stdout` vigente en cada emisión, no en el de la configuración.

    Así sigue funcionando si stdout se reemplaza después (p. ej. la captura de pytest).
    """

    def __init__(self) -> None:
        super().__init__(sys.stdout)

    def emit(self, record: logging.LogRecord) -> None:
        self.stream = sys.stdout
        super().emit(record)


def configure_logging(level: str) -> None:
    """Envía structlog y el logging estándar (uvicorn, SQLAlchemy) a stdout como JSON."""
    structlog.configure(
        processors=[
            *_SHARED_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_SHARED_PROCESSORS,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
    )
    handler = _StdoutHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # uvicorn trae sus propios handlers: se delega en el root para que también salga en JSON.
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True
    # El access log de uvicorn duplicaría el evento http_request del middleware.
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = []
    access_logger.propagate = False


class RequestIdMiddleware:
    """Asigna un `request_id` a cada petición y registra método, ruta, código y duración.

    Middleware ASGI puro: a diferencia de BaseHTTPMiddleware, conserva los contextvars
    en el handler y en los manejadores de error.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # No se limpia al terminar: el manejador de errores 500 se ejecuta fuera de este
        # middleware y debe registrar el mismo request_id. Cada petición corre en su
        # propio contexto, así que no hay fuga entre peticiones.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=str(uuid4()))

        status_code = 500
        started = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            logger.info(
                "http_request",
                method=scope["method"],
                path=scope["path"],
                status_code=status_code,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
