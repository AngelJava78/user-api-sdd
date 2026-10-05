# Investigación y decisiones — Feature 001

Cada decisión resuelve una incógnita del plan. Formato: Decisión · Motivo · Alternativas.

## R-01 Framework HTTP
- **Decisión:** FastAPI + Pydantic v2 + Uvicorn (ADR-0004).
- **Motivo:** async nativo para carga I/O-bound; validación declarativa; OpenAPI integrado.
- **Alternativas:** Django REST Framework, Flask, Litestar.

## R-02 Acceso a datos y migraciones
- **Decisión:** SQLAlchemy 2.0 async + asyncpg + Alembic (ADR-0005).
- **Motivo:** desacopla dominio de SQL; migraciones reversibles.
- **Alternativas:** SQLModel, psycopg 3 con SQL plano, Tortoise ORM.

## R-03 Unicidad case-insensitive del email
- **Decisión:** normalizar a minúsculas en el dominio **y** crear índice único sobre `lower(email)` en PostgreSQL.
- **Motivo:** doble barrera: el dominio da un error claro y la base garantiza la invariante ante concurrencia (dos `POST` simultáneos). La violación de unicidad se traduce a 409.
- **Alternativas:** tipo `CITEXT` (requiere extensión), solo validación en aplicación (no segura ante concurrencia).

## R-04 Paginación
- **Decisión:** `limit`/`offset` (ADR-0007).
- **Alternativas:** keyset/cursor; innecesaria a 1 000 filas.

## R-05 Generación de identificadores
- **Decisión:** UUID v4 generado por la aplicación (dominio), no por la base.
- **Motivo:** la entidad tiene identidad antes de persistirse; facilita pruebas unitarias.
- **Alternativas:** `gen_random_uuid()` en PostgreSQL; UUID v7 (ordenable; considerar si se necesita orden por id).

## R-06 Marcas de tiempo
- **Decisión:** `TIMESTAMPTZ` en UTC; serialización ISO-8601 con zona horaria.
- **Motivo:** evita ambigüedades de zona horaria.

## R-07 Formato de errores de validación
- **Decisión:** reemplazar el manejador por defecto de FastAPI para devolver `Error` con `code = VALIDATION_ERROR` y el detalle por campo en `details`.
- **Motivo:** el contrato exige un único esquema de error (FR-010).

## R-08 Pruebas de contrato
- **Decisión:** Schemathesis contra `spec/openapi/users-api.yaml` usando la app ASGI.
- **Motivo:** detecta deriva entre implementación y contrato canónico.

## R-09 Base de datos en pruebas
- **Decisión:** testcontainers-python con PostgreSQL 17; migraciones Alembic aplicadas al inicio de la sesión; cada prueba en transacción con rollback.
- **Alternativas:** SQLite (no reproduce el comportamiento de PostgreSQL; descartado).

## R-10 Dimensionamiento
- **Decisión:** 2–4 workers Uvicorn, pool de 10 + 5 conexiones por worker.
- **Motivo:** 200 concurrentes en CRUD simple no saturan una instancia; ver `docs/tech-stack.md`.
