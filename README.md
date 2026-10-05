# Users API — Spec-Driven Development

API REST de usuarios construida con Python y PostgreSQL, desarrollada con **Spec-Driven Development (SDD)**:
la especificación precede y gobierna a la implementación.

> Esta entrega contiene solo especificación y estructura. No hay código de aplicación.

## Por dónde empezar

1. `CONSTITUTION.md` — principios no negociables del proyecto.
2. `docs/sdd/workflow.md` — cómo se trabaja con SDD en este repositorio.
   `docs/sdd/guia-claude-code.md` — guía paso a paso para generar el código con Claude Code.
3. `spec/` — especificación viva del sistema (fuente de verdad).
4. `features/001-users-crud/` — primera feature: spec → plan → tareas.
5. `docs/tech-stack.md` — stack tecnológico y dimensionamiento.

## Operaciones

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/users?limit=&offset=` | Lista paginada de usuarios activos |
| `GET` | `/api/v1/users/{user_id}` | Usuario activo o inactivo |
| `POST` | `/api/v1/users` | Crear usuario |
| `PUT` | `/api/v1/users/{user_id}` | Actualizar nombre y apellidos |
| `DELETE` | `/api/v1/users/{user_id}` | Desactivación lógica (idempotente) |
| `GET` | `/api/v1/health/live` | El proceso responde (liveness) |
| `GET` | `/api/v1/health/ready` | Puede recibir tráfico; verifica PostgreSQL (readiness) |

## Stack (propuesto)

Dimensionado para ~1 000 usuarios registrados, 100–200 concurrentes y **disponibilidad 24×7 con SLA de 99 %**.

| Área | Elección |
|---|---|
| Lenguaje | Python 3.13 |
| Framework HTTP | FastAPI + Pydantic v2, servido con Uvicorn (2–4 workers) |
| Base de datos | PostgreSQL 17 |
| Acceso a datos | SQLAlchemy 2.0 async + asyncpg |
| Migraciones | Alembic |
| Logs | structlog (JSON) |
| Pruebas | pytest, httpx, Schemathesis, testcontainers, Locust |
| Calidad | uv, Ruff, mypy --strict, pre-commit |
| Disponibilidad | ≥ 2 réplicas tras balanceador, despliegue rolling, PostgreSQL gestionado con PITR |

Detalle y alternativas en `docs/tech-stack.md` y ADR-0004 a ADR-0008.

## Estructura

```text
users-api-sdd/
├── CONSTITUTION.md          # principios del proyecto
├── AGENTS.md                # reglas para asistentes de IA
├── CLAUDE.md                # instrucciones que Claude Code carga automáticamente
├── .claude/commands/        # comando /tarea para ejecutar tareas SDD
├── consistency-checklist.md # coherencia entre especificaciones
├── spec/                    # especificación viva (fuente de verdad)
│   ├── requirements.md
│   ├── acceptance.md
│   ├── openapi/users-api.yaml
│   ├── domain/user.md
│   └── data/schema.md
├── features/                # especificaciones de cambio, una carpeta por feature
│   └── 001-users-crud/
│       ├── spec.md          # qué y por qué (historias, FR/NFR, escenarios)
│       ├── research.md      # decisiones técnicas y alternativas
│       ├── plan.md          # cómo (stack, estructura, Constitution Check)
│       ├── tasks.md         # tareas test-first trazables
│       ├── quickstart.md    # guion de validación
│       └── checklists/requirements.md
├── docs/
│   ├── architecture.md
│   ├── tech-stack.md
│   ├── testing-strategy.md
│   ├── project-structure.md
│   ├── adr/                 # 0001–0008
│   ├── research/            # comparativas (DRF vs FastAPI)
│   └── sdd/
│       ├── workflow.md
│       └── templates/       # plantillas de spec, plan, tasks, ADR, checklist
├── src/app/                 # capas previstas (sin implementación)
├── tests/                   # contract/, integration/, unit/, load/
├── scripts/
└── infra/                   # Docker Compose y Dockerfile (previstos)
```

## Flujo SDD

1. Constitución → 2. Spec → 3. Aclaraciones → 4. Checklist → 5. Plan → 6. Contratos →
7. Tareas → 8. Implementación test-first → 9. Verificación → 10. Cierre.

Si hay que cambiar el comportamiento, se modifica primero la especificación, nunca solo el código.
