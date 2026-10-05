# Requisitos de la API de Usuarios

## 1. Objetivo

Proporcionar una API REST para administrar usuarios persistidos en PostgreSQL.

## 2. Casos de uso

### UC-01 — Listar usuarios
Un cliente puede obtener una colección paginada (`limit`/`offset`) de usuarios activos.

### UC-02 — Obtener usuario
Un cliente puede consultar un usuario mediante su identificador. Los usuarios activos e inactivos pueden consultarse por identificador.

### UC-03 — Crear usuario
Un cliente puede crear un usuario proporcionando los campos obligatorios definidos por el contrato. Los usuarios nuevos se crean activos.

### UC-04 — Actualizar usuario
Un cliente puede actualizar los datos modificables de un usuario existente. El email, el identificador y el status no se modifican mediante `PUT`.

### UC-05 — Desactivar usuario
Un cliente puede desactivar un usuario existente mediante `DELETE`. La operación es lógica: conserva el registro y establece `status = false`.

## 3. Reglas funcionales

- Cada usuario debe tener un identificador único.
- El correo electrónico debe ser único sin distinguir mayúsculas/minúsculas.
- El correo electrónico se normaliza (sin espacios en los extremos, en minúsculas) y es inmutable después de la creación.
- Los campos obligatorios deben validarse antes de persistir.
- `name` es obligatorio y tiene un máximo de 30 caracteres.
- `lastname` es obligatorio y tiene un máximo de 30 caracteres.
- `second_lastname` es opcional y tiene un máximo de 30 caracteres.
- `second_lastname` representa el apellido materno.
- `lastname` representa el apellido paterno.
- Un usuario nuevo inicia con `status = true`.
- `status = true` representa ACTIVE y `status = false` representa INACTIVE.
- Un recurso inexistente debe producir una respuesta HTTP de recurso no encontrado.
- Una solicitud inválida debe producir una respuesta HTTP de validación.
- Un intento de crear un usuario con un correo ya registrado debe producir un conflicto.
- `DELETE` sobre un usuario inexistente no debe tratarse como una desactivación exitosa.
- `DELETE` no elimina físicamente el registro.
- `DELETE` sobre un usuario ya inactivo responde 204 sin cambios (idempotente).
- `GET /users` devuelve únicamente usuarios activos.
- `GET /users/{user_id}` permite consultar usuarios activos e inactivos.
- Las respuestas deben seguir el contrato OpenAPI.

## 4. No funcionales

Carga prevista: ~1 000 usuarios registrados y 100–200 usuarios concurrentes.

- p95 de latencia < 200 ms en lecturas y < 300 ms en escrituras con 200 usuarios concurrentes.
- Tasa de errores 5xx < 0,1 % bajo esa carga.
- **Disponibilidad 24×7 con SLA mensual de 99 %** (presupuesto de caída: ~7 h 18 min al mes, ~87 h 36 min al año).
- Los despliegues y las migraciones no deben interrumpir el servicio.
- Backups automáticos de PostgreSQL con restauración a un punto en el tiempo; RPO ≤ 15 min y RTO ≤ 1 h.
- La API debe ser stateless.
- La persistencia debe realizarse en PostgreSQL.
- La configuración sensible no debe almacenarse en el repositorio.
- Los errores deben tener un formato consistente.
- Las operaciones críticas deben ser observables mediante logs.
- La API debe disponer de pruebas de contrato e integración.
- Las migraciones de base de datos deben ser reproducibles.

## 5. Decisiones tomadas (propuestas)

| Tema | Decisión | Referencia |
|---|---|---|
| Framework HTTP | FastAPI + Pydantic v2 + Uvicorn | ADR-0004 |
| Acceso a datos y migraciones | SQLAlchemy 2.0 async + asyncpg + Alembic | ADR-0005 |
| Herramientas | uv, Ruff, mypy, pytest | ADR-0006 |
| Paginación de `GET /users` | `limit`/`offset` (20 por defecto, máx. 100) | ADR-0007 |
| Caracteres en nombres | Letras Unicode, espacios, guion, apóstrofo; empieza con letra | `spec/domain/user.md` |
| `DELETE` sobre inactivo | 204, idempotente | `spec/acceptance.md` |
| Reactivación | Fuera de alcance en la versión 1 | `features/001-users-crud/spec.md` |
| Disponibilidad | ≥ 2 réplicas tras balanceador, PostgreSQL gestionado, despliegue rolling | ADR-0008 |
| Versionado de API | Prefijo de ruta `/api/v1`; cambios incompatibles → `/api/v2` | `spec/openapi/users-api.yaml` |

## 6. Decisiones pendientes

- [NEEDS CLARIFICATION] Estrategia de autenticación/autorización.
- [NEEDS CLARIFICATION] Límites de rate limiting.
