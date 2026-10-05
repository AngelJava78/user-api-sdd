# Tareas — Feature 001: Gestión de usuarios

**Entradas:** `spec.md`, `plan.md`, `research.md`, `spec/openapi/users-api.yaml`, `spec/data/schema.md`

**Formato:** `[ID] [P?] [Historia] Descripción (requisitos)`
- `[P]`: puede ejecutarse en paralelo (archivos distintos, sin dependencias).
- Las pruebas de cada historia se escriben **antes** y deben **fallar** antes de implementar (Principio III).

## Fase 1 — Preparación

- [x] T001 Inicializar proyecto con uv y Python 3.13; completar `pyproject.toml` con dependencias de `docs/tech-stack.md`.
- [x] T002 [P] Configurar Ruff, mypy --strict, pytest y cobertura en `pyproject.toml`; añadir `.pre-commit-config.yaml`.
- [x] T003 [P] Crear `infra/docker-compose.yml` con PostgreSQL 17 y `infra/Dockerfile` de la API. (NFR-003)
- [x] T004 [P] Definir `Settings` en `src/app/config.py` leyendo `.env`. (NFR-005)
- [x] T005 Configurar pipeline de CI: lint → typecheck → unit → integración/contrato.

## Fase 2 — Fundamentos (bloquea todas las historias)

- [ ] T006 Configurar Alembic en `src/app/infrastructure/database/migrations/`.
- [ ] T007 Migración inicial: tabla `users`, índice único `lower(email)`, índice `(status, created_at, id)`. (FR-004, NFR-006)
- [ ] T008 Prueba de integración: `upgrade` sobre base vacía y `downgrade` completo. (NFR-006)
- [ ] T009 [P] Engine async, sessionmaker y pool configurable. (ADR-0005)
- [ ] T010 [P] Errores de dominio y manejadores HTTP que devuelvan el esquema `Error`. (FR-010)
- [ ] T011 [P] Logging structlog + middleware `request_id`. (NFR-004)
- [ ] T012 [P] `tests/conftest.py`: contenedor PostgreSQL, app, cliente httpx, rollback por prueba.
- [ ] T013 Prueba + implementación de `GET /health/live` y `GET /health/ready` (503 si la base no responde). (FR-011, NFR-008)
- [ ] T014 Prueba de contrato base con Schemathesis (inicialmente en rojo). (SC-002)

## Fase 3 — US-1 Registrar usuario (P1) 🎯 MVP

### Pruebas (primero)
- [ ] T015 [P] [US1] Unit: value object `Email` (normalización, formato). (FR-005)
- [ ] T016 [P] [US1] Unit: value object `PersonName` (1–30, caracteres permitidos). (FR-006)
- [ ] T017 [P] [US1] Unit: caso de uso `create_user` con repositorio en memoria (activo, duplicado). (FR-003, FR-004)
- [ ] T018 [P] [US1] Integración: `POST /users` → 201, 409 case-insensitive, 422. (FR-003, FR-004, FR-006)
- [ ] T019 [US1] Integración: dos `POST` concurrentes con el mismo email → uno 201, otro 409. (FR-004)

### Implementación
- [ ] T020 [US1] Entidad `User` y value objects en `domain/`.
- [ ] T021 [US1] Protocolo `UserRepository` en `domain/repository.py`.
- [ ] T022 [US1] `SqlAlchemyUserRepository.add` traduciendo `IntegrityError` → `EmailAlreadyExists`.
- [ ] T023 [US1] Caso de uso `create_user` y endpoint `POST /users`.

## Fase 4 — US-2 Consultar usuarios (P1)

### Pruebas (primero)
- [ ] T024 [P] [US2] Unit: `list_users` y `get_user`. (FR-001, FR-002)
- [ ] T025 [P] [US2] Integración: `GET /users` solo activos, paginación, límites 422. (FR-001)
- [ ] T026 [P] [US2] Integración: `GET /users/{id}` activo, inactivo, 404, id no UUID 422. (FR-002)

### Implementación
- [ ] T027 [US2] Repositorio: `get_by_id`, `list_active(limit, offset)`, `count_active`.
- [ ] T028 [US2] Casos de uso y endpoints `GET /users`, `GET /users/{user_id}`.

## Fase 5 — US-3 Actualizar usuario (P2)

### Pruebas (primero)
- [ ] T029 [P] [US3] Unit: `update_user` no altera email/status; actualiza `updated_at`. (FR-005, FR-007)
- [ ] T030 [P] [US3] Integración: `PUT` 200, 404, 422, campos extra 422, `second_lastname: null`. (FR-006, FR-007)

### Implementación
- [ ] T031 [US3] Repositorio `update` y caso de uso `update_user`.
- [ ] T032 [US3] Endpoint `PUT /users/{user_id}`.

## Fase 6 — US-4 Desactivar usuario (P2)

### Pruebas (primero)
- [ ] T033 [P] [US4] Unit: `deactivate` idempotente. (FR-008, FR-009)
- [ ] T034 [P] [US4] Integración: `DELETE` 204, repetido 204, 404, registro conservado. (FR-008, FR-009)

### Implementación
- [ ] T035 [US4] Caso de uso `deactivate_user` y endpoint `DELETE /users/{user_id}`.

## Fase 7 — Validación y cierre

- [ ] T036 Schemathesis en verde contra todo el contrato. (SC-002)
- [ ] T037 [P] `tests/load/locustfile.py`: 200 usuarios, mezcla 80 % lecturas / 20 % escrituras. (NFR-001, NFR-002)
- [ ] T038 [P] Verificar cobertura ≥ 90 % en `domain/` y `application/`. (NFR-007)
- [ ] T039 Ejecutar `quickstart.md` de principio a fin.
- [ ] T040 Actualizar `consistency-checklist.md` y marcar ADR-0004…0008 como Aceptados.

## Fase 8 — Disponibilidad y operación (SLA 99 %)

- [ ] T041 Prueba de integración: apagado ordenado con `SIGTERM` termina peticiones en curso y `/health/ready` pasa a 503. (NFR-009)
- [ ] T042 [P] Elegir plataforma de despliegue y PostgreSQL gestionado; registrar la decisión en ADR-0008. (NFR-008, NFR-011)
- [ ] T043 [P] Definir pipeline de despliegue: migraciones expand/contract → despliegue rolling con 2 réplicas. (NFR-009)
- [ ] T044 Prueba: Locust con 200 usuarios durante un despliegue rolling, 0 errores 5xx. (NFR-009)
- [ ] T045 Prueba de caos: detener una réplica bajo carga sin pérdida de servicio. (NFR-010)
- [ ] T046 [P] Configurar monitor externo de `/health/ready`, métricas de p95/5xx y alertas al 50 % del presupuesto de caída. (NFR-008, NFR-012)
- [ ] T047 Simulacro de restauración PITR y registro del RTO obtenido. (NFR-011)

## Dependencias

- Fase 1 → Fase 2 → (US-1 → US-2) → (US-3, US-4 en paralelo) → Fase 7 → Fase 8.
- US-2 depende de US-1 solo para disponer de datos en pruebas; puede usar fixtures.

## Matriz de trazabilidad

| Requisito | Pruebas | Implementación |
|---|---|---|
| FR-001 | T024, T025 | T027, T028 |
| FR-002 | T024, T026 | T027, T028 |
| FR-003 | T017, T018 | T020, T023 |
| FR-004 | T017, T018, T019 | T007, T022 |
| FR-005 | T015, T029 | T020 |
| FR-006 | T016, T018, T030 | T020 |
| FR-007 | T029, T030 | T031, T032 |
| FR-008 | T033, T034 | T035 |
| FR-009 | T033, T034 | T035 |
| FR-010 | T014, T036 | T010 |
| FR-011 | T013 | T013 |
| NFR-008 | T013, T046 | T042, T046 |
| NFR-009 | T041, T044 | T043 |
| NFR-010 | T045 | T042 |
| NFR-011 | T047 | T042 |
| NFR-012 | T046 | T046 |
| NFR-001/002 | T037 | — |
| NFR-004 | T011 | T011 |
| NFR-006 | T008 | T006, T007 |
| NFR-007 | T038 | — |
