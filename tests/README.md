# Tests

Esta carpeta contiene únicamente la estructura prevista. Herramientas en `docs/testing-strategy.md`.

- `contract/`: pruebas derivadas del contrato OpenAPI (Schemathesis).
- `integration/`: pruebas contra PostgreSQL real (testcontainers).
- `unit/`: pruebas de dominio y aplicación (repositorio en memoria).
- `load/`: pruebas de carga (Locust) para NFR-001/NFR-002.

La implementación de pruebas se realizará después de cerrar la especificación, siguiendo
`features/001-users-crud/tasks.md` (las pruebas se escriben antes que el código).
