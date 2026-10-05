# Quickstart — Validación manual de la Feature 001

> Guion para comprobar, una vez implementada la feature, que el sistema cumple la especificación.
> Cada paso indica el escenario de `spec.md` que valida.

## Preparación

1. Copiar `.env.example` a `.env` y completar `DATABASE_URL`.
2. Levantar PostgreSQL: `docker compose -f infra/docker-compose.yml up -d db`.
3. Instalar dependencias: `uv sync`.
4. Aplicar migraciones: `uv run alembic upgrade head`.
5. Arrancar la API: `uv run uvicorn app.main:app --workers 2`.

## Escenarios

| Paso | Petición | Resultado esperado | Escenario |
|---|---|---|---|
| 1 | `GET /api/v1/health/live` y `GET /api/v1/health/ready` | 200 `{"status":"ok"}` | FR-011 |
| 1b | Detener `db` y repetir `GET /api/v1/health/ready` | 503 `SERVICE_UNAVAILABLE` | FR-011 |
| 2 | `POST /api/v1/users` con `{"email":" Ana@Mail.com ","name":"Ana","lastname":"López"}` | 201, `email = "ana@mail.com"`, `status = true` | US-1 #1, #4 |
| 3 | Repetir paso 2 con `ana@mail.com` | 409 `EMAIL_ALREADY_EXISTS` | US-1 #2 |
| 4 | `GET /api/v1/users` | 200, `total = 1` | US-2 #1 |
| 5 | `PUT /api/v1/users/{id}` con `{"name":"Ana María","lastname":"López"}` | 200, `name` actualizado | US-3 #1 |
| 6 | `PUT` con `{"name":"Ana","lastname":"López","email":"x@y.com"}` | 422 | US-3 #2 |
| 7 | `DELETE /api/v1/users/{id}` | 204 | US-4 #1 |
| 8 | Repetir paso 7 | 204 | US-4 #2 |
| 9 | `GET /api/v1/users/{id}` | 200, `status = false` | US-2 #4 |
| 10 | `GET /api/v1/users` | 200, `total = 0` | US-4 #1 |

## Pruebas automatizadas

- `uv run pytest` — unitarias, integración y contrato.
- `uv run locust -f tests/load/locustfile.py --users 200 --spawn-rate 20` — NFR-001/002.
