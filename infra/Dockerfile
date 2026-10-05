# Imagen de la API (NFR-003: sin estado, escalable horizontalmente).
# Construir desde la raíz del repositorio:
#   docker build -f infra/Dockerfile -t users-api .

# --- Etapa de construcción: resuelve dependencias con uv a partir de uv.lock ---
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Capa de dependencias: solo se reconstruye si cambia el lockfile.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

# --- Etapa de ejecución ---
FROM python:3.13-slim

RUN useradd --create-home --uid 10001 app

WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 8000

# Forma exec: uvicorn es el PID 1 y recibe SIGTERM para el apagado ordenado (ADR-0008).
# El número de workers se toma de WEB_CONCURRENCY.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
