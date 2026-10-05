# Stack tecnológico

**Estado:** Propuesto (pendiente de aprobación) · Ver ADR-0004 a ADR-0008.

## Contexto de carga

| Métrica | Valor estimado | Implicación |
|---|---|---|
| Usuarios registrados | ~1 000 | La tabla cabe completa en memoria de PostgreSQL; índices simples bastan. |
| Usuarios concurrentes | 100–200 | Carga moderada: 2 workers ASGI por instancia bastan; se usan 2 instancias por disponibilidad. |
| Tipo de carga | CRUD, I/O-bound | Un stack asíncrono aprovecha mejor la espera de base de datos. |

Conclusión: no se necesitan caché (Redis), réplicas de lectura, colas ni PgBouncer. Sí se necesitan al menos 2 réplicas de la API por el SLA de 99 % (ADR-0008). Se priorizan
simplicidad, tipado y buen soporte de OpenAPI (Principio VI de la constitución).

## Stack propuesto

| Área | Elección | Versión objetivo | Motivo |
|---|---|---|---|
| Lenguaje | Python | 3.13 | Estable, soporte amplio de librerías, mejoras de rendimiento. |
| Framework HTTP | **FastAPI** | 0.11x+ | Async nativo, validación con Pydantic, OpenAPI integrado, muy documentado. |
| Validación / esquemas | **Pydantic v2** | 2.x | Núcleo en Rust, rápido; mapea 1:1 con los esquemas del contrato. |
| Configuración | **pydantic-settings** | 2.x | Lee variables de entorno tipadas (`.env`). |
| Servidor ASGI | **Uvicorn** (con `--workers`) | 0.3x+ | 2–4 workers cubren 200 concurrentes con holgura. |
| Base de datos | **PostgreSQL** | 17 | Requisito del proyecto (ADR-0003). |
| ORM / acceso a datos | **SQLAlchemy 2.0** (modo async) | 2.0.x | Tipado moderno, Unit of Work, desacopla dominio de SQL. |
| Driver | **asyncpg** | 0.30+ | Driver async más rápido para PostgreSQL. |
| Migraciones | **Alembic** | 1.13+ | Estándar para SQLAlchemy; migraciones reversibles. |
| Logs | **structlog** | 24+ | Logs JSON estructurados con `request_id`. |
| Gestor de paquetes | **uv** | 0.x | Rápido, lockfile reproducible, gestiona la versión de Python. |
| Lint + formato | **Ruff** | 0.x | Sustituye flake8/isort/black en una sola herramienta. |
| Tipado estático | **mypy** (`--strict`) | 1.x | Refuerza contratos entre capas. |
| Hooks | **pre-commit** | 3.x | Ejecuta Ruff/mypy antes de cada commit. |

## Pruebas

| Tipo | Herramienta | Uso |
|---|---|---|
| Runner | **pytest** + **pytest-asyncio** | Base de todas las pruebas. |
| Cliente HTTP de pruebas | **httpx** (`AsyncClient` + `ASGITransport`) | Llamar a la app sin levantar servidor. |
| Contrato | **Schemathesis** | Genera casos desde `users-api.yaml` y verifica que la API cumple el contrato. |
| Integración | **testcontainers-python** (PostgreSQL) | PostgreSQL real y efímero por sesión de pruebas. |
| Cobertura | **pytest-cov** | Umbral mínimo 90 % en `domain/` y `application/`. |
| Carga | **Locust** | Valida NFR-001/NFR-002 con 200 usuarios concurrentes. |

## Infraestructura local

- **Docker Compose**: servicios `api` y `db` (PostgreSQL 17).
- **CI** (GitHub Actions u otro): lint → typecheck → tests unitarios → tests de integración/contrato.

## Dimensionamiento inicial

| Parámetro | Valor | Razonamiento |
|---|---|---|
| Réplicas de la API | 2 (mínimo, por disponibilidad) | Ver sección Disponibilidad y ADR-0008. |
| Workers Uvicorn por réplica | 2 | Cada worker async atiende cientos de conexiones. |
| `DB_POOL_SIZE` por worker | 10 | 2 réplicas × 2 workers × (10 + 5) = 60 conexiones máximo. |
| `DB_MAX_OVERFLOW` | 5 | Absorbe picos sin agotar PostgreSQL. |
| `max_connections` de PostgreSQL | 100 (por defecto) | Suficiente con el cálculo anterior. |
| `DB_POOL_TIMEOUT` | 5 s | Falla rápido en lugar de encolar indefinidamente. |

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| Django + DRF | Más pesado; su ORM y admin no aportan valor a una API de un solo recurso. |
| Flask | Sin async nativo ni OpenAPI integrado; requiere más extensiones. |
| Litestar | Muy buena opción técnica, pero menor comunidad y material de aprendizaje. |
| SQLModel | Mezcla modelo de API y de persistencia, lo que choca con la arquitectura por capas (ADR-0001). |
| psycopg 3 sin ORM | Válido, pero más SQL manual; SQLAlchemy facilita Unit of Work y migraciones con Alembic. |
| Poetry | uv es más rápido y también gestiona versiones de Python. |

## Disponibilidad (SLA 99 %, 24×7)

Ver ADR-0008. Presupuesto de caída: ~7 h 18 min al mes.

| Componente | Elección | Por qué |
|---|---|---|
| Réplicas de la API | ≥ 2, detrás de balanceador | La caída de una réplica o un despliegue no interrumpe el servicio. |
| Health checks | `/health/live` y `/health/ready` | Reinicio automático y retirada del tráfico de réplicas no sanas. |
| Despliegue | Rolling o blue/green | Sin ventanas de mantenimiento. |
| Base de datos | PostgreSQL gestionado con backups y PITR | RPO ≤ 15 min, RTO ≤ 1 h sin operar la base a mano. |
| Migraciones | Alembic con patrón expand/contract | Cambios de esquema sin detener la API. |
| Monitoreo | Monitor externo de uptime + métricas + alertas | Medir el SLA y avisar antes de agotar el presupuesto. |

Con 2 réplicas de 2 workers cada una: 2 × 2 × (10 + 5) = 60 conexiones máximo a PostgreSQL. Durante un
despliegue rolling conviven temporalmente réplicas nuevas y viejas, por lo que conviene dejar margen
(`max_connections` ≥ 100).
