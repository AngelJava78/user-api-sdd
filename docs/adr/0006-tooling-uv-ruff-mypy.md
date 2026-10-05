# ADR-0006 — Herramientas de desarrollo: uv, Ruff, mypy, pytest

## Estado

Propuesto

## Contexto

La constitución exige puertas de calidad automáticas y builds reproducibles.

## Decisión

- **uv** para dependencias, lockfile (`uv.lock`) y versión de Python.
- **Ruff** para lint y formato.
- **mypy --strict** para tipado.
- **pytest**, **pytest-asyncio**, **httpx**, **Schemathesis**, **testcontainers-python**, **pytest-cov** para pruebas.
- **Locust** para pruebas de carga.
- **pre-commit** para ejecutar Ruff y mypy localmente.

## Consecuencias

- Un único `pyproject.toml` concentra dependencias y configuración de herramientas.
- Las pruebas de integración requieren Docker disponible (testcontainers).
