# Plan de implementación — Feature 001: Gestión de usuarios

**Especificación:** `spec.md` · **Investigación:** `research.md` · **Tareas:** `tasks.md`

> El plan describe **cómo** se construirá la feature. No contiene código; define stack,
> estructura, contratos y orden de trabajo.

## Resumen

API REST asíncrona en FastAPI sobre PostgreSQL con arquitectura por capas. El contrato
`spec/openapi/users-api.yaml` es canónico; las pruebas de contrato verifican su cumplimiento.

## Contexto técnico

| Aspecto | Valor |
|---|---|
| Lenguaje | Python 3.13 |
| Dependencias principales | FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2.0 (async), asyncpg, Alembic, structlog, Uvicorn |
| Almacenamiento | PostgreSQL 17 |
| Pruebas | pytest, pytest-asyncio, httpx, Schemathesis, testcontainers-python, pytest-cov, Locust |
| Calidad | uv, Ruff, mypy --strict, pre-commit |
| Plataforma | Contenedores Docker Linux en plataforma gestionada (por decidir) + PostgreSQL gestionado |
| Tipo de proyecto | Servicio web (API única) |
| Objetivos de rendimiento | p95 < 200 ms lecturas / < 300 ms escrituras con 200 concurrentes |
| Escala | ~1 000 usuarios, 100–200 concurrentes |
| Disponibilidad | 24×7, SLA mensual 99 %; ≥ 2 réplicas, despliegue rolling (ADR-0008) |
| Restricciones | Stateless; sin borrado físico; email inmutable; migraciones expand/contract |

## Constitution Check

| Principio | Cumple | Evidencia |
|---|---|---|
| I. Especificación como fuente de verdad | ✅ | `spec.md` y `spec/` cerrados antes de tareas. |
| II. Contrato primero | ✅ | `users-api.yaml` actualizado (paginación, health, errores). |
| III. Pruebas primero | ✅ | En `tasks.md` las pruebas preceden a la implementación. |
| IV. Dominio independiente | ✅ | `domain/` sin dependencias de framework (ver estructura). |
| V. Trazabilidad | ✅ | FR/NFR enlazados en tareas. |
| VI. Simplicidad | ✅ | Sin caché, colas ni PgBouncer (justificado por la escala). |
| VII. Seguridad y configuración | ⚠️ | Autenticación pendiente (`[NEEDS CLARIFICATION]`); aceptable solo para entornos no productivos. |
| VIII. Observabilidad | ✅ | structlog + `request_id` + `/health/live` y `/health/ready` + monitor de uptime. |
| IX. Decisiones documentadas | ✅ | ADR-0004 a ADR-0008. |
| X. Disponibilidad | ✅ | 2 réplicas, apagado ordenado, despliegue rolling, PITR (ADR-0008). |

## Estructura del código (prevista)

```text
src/app/
├── main.py                      # creación de la app FastAPI, routers, manejadores de error
├── config.py                    # Settings (pydantic-settings)
├── api/
│   ├── routes/users.py          # endpoints /users
│   ├── routes/health.py         # /health/live y /health/ready
│   ├── schemas.py               # modelos Pydantic de request/response (espejo del contrato)
│   ├── errors.py                # mapeo de excepciones de dominio → Error HTTP
│   └── dependencies.py          # inyección de casos de uso y sesión
├── application/
│   ├── use_cases/               # list_users, get_user, create_user, update_user, deactivate_user
│   └── dto.py                   # datos de entrada/salida de casos de uso
├── domain/
│   ├── user.py                  # entidad User e invariantes
│   ├── value_objects.py         # Email, PersonName
│   ├── errors.py                # UserNotFound, EmailAlreadyExists, InvalidUserData
│   └── repository.py            # protocolo UserRepository
└── infrastructure/
    ├── database/
    │   ├── engine.py            # engine async y sessionmaker
    │   ├── models.py            # modelo ORM UserModel
    │   └── migrations/          # Alembic (env.py, versions/)
    ├── repositories/
    │   └── sqlalchemy_user_repository.py
    └── logging.py               # configuración structlog + middleware request_id

tests/
├── conftest.py                  # app, cliente httpx, contenedor PostgreSQL
├── contract/                    # Schemathesis contra el contrato
├── integration/                 # API + PostgreSQL real
├── unit/                        # dominio y casos de uso con repositorio en memoria
└── load/                        # locustfile
```

## Diseño por capas

- **API** valida forma (Pydantic), invoca un caso de uso y traduce errores de dominio a HTTP:
  `InvalidUserData → 422`, `UserNotFound → 404`, `EmailAlreadyExists → 409`.
- **Application** orquesta: un caso de uso por operación; recibe el repositorio por inyección.
- **Domain** contiene `User`, los value objects y las reglas (normalización de email, reglas de nombres, desactivación idempotente).
- **Infrastructure** implementa `UserRepository` con SQLAlchemy; traduce `IntegrityError` de unicidad a `EmailAlreadyExists`.

## Disponibilidad

- Lifespan de FastAPI: al arrancar abre el pool; al recibir `SIGTERM` marca la réplica como no lista, espera las peticiones en curso (`SHUTDOWN_GRACE_SECONDS`) y cierra el pool.
- `/health/ready` hace `SELECT 1` con timeout `READINESS_DB_TIMEOUT_SECONDS`.
- Las migraciones se ejecutan como paso previo del pipeline de despliegue, no en el arranque de cada réplica.

## Fases

1. **Fase 0 — Investigación:** `research.md` (completada).
2. **Fase 1 — Diseño:** contrato, modelo de datos y quickstart actualizados (`spec/`, `quickstart.md`).
3. **Fase 2 — Tareas:** `tasks.md`.
4. **Fase 3 — Implementación:** siguiendo `tasks.md` en orden test-first.
5. **Fase 4 — Validación:** pruebas, Schemathesis, Locust y `quickstart.md`.
6. **Fase 5 — Operación:** despliegue con 2 réplicas, monitoreo del SLA y simulacro de restauración.

## Complexity Tracking

| Complejidad añadida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Separación modelo ORM / entidad de dominio | Principio IV (dominio independiente) | SQLModel único: acopla capas |
| ≥ 2 réplicas + balanceador | NFR-008/009/010 (SLA 99 %) | Una sola instancia: cada despliegue es una caída |
| Migraciones expand/contract | NFR-009 (despliegues sin interrupción) | Migración destructiva única: requiere parar la API |
| Testcontainers en pruebas | Reproducir PostgreSQL real (índice `lower(email)`) | SQLite: comportamiento distinto |
