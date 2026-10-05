# Estructura del proyecto

```text
users-api-sdd/
├── README.md
├── CONSTITUTION.md
├── AGENTS.md
├── CLAUDE.md
├── .claude/
│   └── commands/
│       └── tarea.md
├── consistency-checklist.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── spec/                         # especificación viva del sistema
│   ├── requirements.md
│   ├── acceptance.md
│   ├── openapi/
│   │   └── users-api.yaml
│   ├── domain/
│   │   └── user.md
│   └── data/
│       └── schema.md
├── features/                     # especificaciones de cambio
│   └── 001-users-crud/
│       ├── spec.md
│       ├── research.md
│       ├── plan.md
│       ├── tasks.md
│       ├── quickstart.md
│       └── checklists/
│           └── requirements.md
├── docs/
│   ├── architecture.md
│   ├── tech-stack.md
│   ├── testing-strategy.md
│   ├── project-structure.md
│   ├── adr/
│   │   ├── 0001-architecture-style.md
│   │   ├── 0002-openapi-as-source-of-truth.md
│   │   ├── 0003-postgresql-persistence.md
│   │   ├── 0004-fastapi-http-framework.md
│   │   ├── 0005-sqlalchemy-asyncpg-alembic.md
│   │   ├── 0006-tooling-uv-ruff-mypy.md
│   │   ├── 0007-pagination-limit-offset.md
│   │   └── 0008-availability-and-deployment.md
│   ├── research/
│   │   └── drf-vs-fastapi.md
│   └── sdd/
│       ├── workflow.md
│       ├── guia-claude-code.md
│       └── templates/
│           ├── feature-spec-template.md
│           ├── plan-template.md
│           ├── tasks-template.md
│           ├── checklist-template.md
│           └── adr-template.md
├── src/
│   └── app/
│       ├── api/
│       ├── application/
│       ├── domain/
│       └── infrastructure/
│           ├── database/
│           └── repositories/
├── tests/
│   ├── contract/
│   ├── integration/
│   ├── unit/
│   └── load/
├── scripts/
└── infra/
```

Los directorios de `src/` están preparados para la implementación posterior y no contienen código de negocio en esta entrega.
La estructura detallada de módulos prevista está en `features/001-users-crud/plan.md`.
