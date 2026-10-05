# Feature 001 — Gestión de usuarios (CRUD)

**Estado:** Borrador para revisión · **Creada:** 2026-10-05 · **Rama sugerida:** `001-users-crud`

> Esta especificación describe **qué** debe hacer el sistema y **por qué**, no cómo.
> Las decisiones técnicas viven en `plan.md`. La especificación viva consolidada del sistema
> está en `spec/`; esta feature la referencia y no la duplica.

## Referencias

- Requisitos del sistema: `spec/requirements.md`
- Dominio: `spec/domain/user.md`
- Contrato HTTP: `spec/openapi/users-api.yaml`
- Modelo de datos: `spec/data/schema.md`
- Criterios de aceptación: `spec/acceptance.md`

## Historias de usuario

### US-1 — Registrar un usuario (Prioridad P1)
Como cliente de la API quiero crear un usuario con su email y nombre completo para que quede registrado y activo.

**Prueba independiente:** con una base vacía, `POST /users` devuelve 201 y luego `GET /users/{id}` devuelve el mismo usuario.

**Escenarios de aceptación**
1. **Dado** un payload válido, **cuando** hago `POST /users`, **entonces** recibo 201, el usuario con `status = true` y `id` UUID.
2. **Dado** un usuario con email `Ana@Mail.com`, **cuando** creo otro con `ana@mail.com`, **entonces** recibo 409 `EMAIL_ALREADY_EXISTS`.
3. **Dado** un `name` de 31 caracteres, **cuando** hago `POST /users`, **entonces** recibo 422 `VALIDATION_ERROR`.
4. **Dado** un email con espacios y mayúsculas, **cuando** lo creo, **entonces** se almacena sin espacios y en minúsculas.

### US-2 — Consultar usuarios (Prioridad P1)
Como cliente quiero listar los usuarios activos y consultar cualquier usuario por su id.

**Escenarios de aceptación**
1. **Dado** 3 usuarios activos y 1 inactivo, **cuando** hago `GET /users`, **entonces** recibo 200 con 3 elementos y `total = 3`.
2. **Dado** 25 usuarios activos, **cuando** hago `GET /users?limit=10&offset=20`, **entonces** recibo 5 elementos y `total = 25`.
3. **Dado** `limit=101`, **cuando** hago `GET /users`, **entonces** recibo 422.
4. **Dado** un usuario inactivo, **cuando** hago `GET /users/{id}`, **entonces** recibo 200 con `status = false`.
5. **Dado** un UUID inexistente, **cuando** hago `GET /users/{id}`, **entonces** recibo 404 `USER_NOT_FOUND`.
6. **Dado** un `user_id` que no es UUID, **cuando** hago `GET /users/abc`, **entonces** recibo 422.

### US-3 — Actualizar datos personales (Prioridad P2)
Como cliente quiero actualizar nombre y apellidos de un usuario sin alterar su email ni su estado.

**Escenarios de aceptación**
1. **Dado** un usuario existente, **cuando** hago `PUT` con `name`, `lastname` válidos, **entonces** recibo 200, los campos cambian y `updated_at` aumenta.
2. **Dado** un payload que incluye `email` o `status`, **cuando** hago `PUT`, **entonces** recibo 422 (campos no permitidos).
3. **Dado** un UUID inexistente, **cuando** hago `PUT`, **entonces** recibo 404.
4. **Dado** `second_lastname: null`, **cuando** hago `PUT`, **entonces** el apellido materno queda vacío (`null`).

### US-4 — Desactivar un usuario (Prioridad P2)
Como cliente quiero desactivar un usuario sin perder su registro.

**Escenarios de aceptación**
1. **Dado** un usuario activo, **cuando** hago `DELETE /users/{id}`, **entonces** recibo 204 y deja de aparecer en `GET /users`.
2. **Dado** un usuario ya inactivo, **cuando** repito `DELETE`, **entonces** recibo 204 (operación idempotente).
3. **Dado** un UUID inexistente, **cuando** hago `DELETE`, **entonces** recibo 404.
4. **Dado** un usuario desactivado, **cuando** consulto la base de datos, **entonces** el registro sigue existiendo.

## Requisitos funcionales

| ID | Requisito | Historia |
|---|---|---|
| FR-001 | El sistema DEBE listar solo usuarios activos, paginados por `limit`/`offset`, con orden estable. | US-2 |
| FR-002 | El sistema DEBE devolver un usuario por `id`, activo o inactivo, o 404 si no existe. | US-2 |
| FR-003 | El sistema DEBE crear usuarios activos con `id` UUID generado por el sistema. | US-1 |
| FR-004 | El sistema DEBE rechazar con 409 un email ya registrado, sin distinguir mayúsculas/minúsculas. | US-1 |
| FR-005 | El sistema DEBE normalizar el email (recortar espacios, minúsculas) y tratarlo como inmutable. | US-1, US-3 |
| FR-006 | El sistema DEBE validar `name`, `lastname` (obligatorios) y `second_lastname` (opcional): 1–30 caracteres según las reglas de `spec/domain/user.md`. | US-1, US-3 |
| FR-007 | `PUT` DEBE modificar solo `name`, `lastname`, `second_lastname` y rechazar cualquier otro campo. | US-3 |
| FR-008 | `DELETE` DEBE desactivar lógicamente (`status = false`) sin borrar el registro. | US-4 |
| FR-009 | `DELETE` sobre un usuario ya inactivo DEBE responder 204 sin cambios. | US-4 |
| FR-010 | Todos los errores DEBEN usar el esquema `Error` con códigos estables (`VALIDATION_ERROR`, `USER_NOT_FOUND`, `EMAIL_ALREADY_EXISTS`, `SERVICE_UNAVAILABLE`, `INTERNAL_ERROR`, `NOT_FOUND`, `METHOD_NOT_ALLOWED`). | Todas |
| FR-011 | El sistema DEBE exponer `GET /health/live` (proceso vivo) y `GET /health/ready` (puede recibir tráfico; verifica PostgreSQL). | Operación |

## Requisitos no funcionales

| ID | Requisito | Cómo se verifica |
|---|---|---|
| NFR-001 | p95 de latencia < 200 ms en lecturas y < 300 ms en escrituras con 200 usuarios concurrentes. | Prueba de carga con Locust. |
| NFR-002 | Tasa de errores 5xx < 0,1 % durante la prueba de carga. | Prueba de carga con Locust. |
| NFR-003 | La API es stateless; puede escalar horizontalmente sin cambios. | Revisión de diseño. |
| NFR-004 | Logs JSON con `request_id`, método, ruta, código y duración. | Prueba de integración + revisión. |
| NFR-005 | Ningún secreto en el repositorio; configuración por variables de entorno. | Revisión + escáner de secretos. |
| NFR-006 | Migraciones reproducibles (`upgrade` sobre base vacía) y reversibles (`downgrade`). | Prueba de integración. |
| NFR-007 | Cobertura ≥ 90 % en `domain/` y `application/`. | `pytest-cov` en CI. |
| NFR-008 | Disponibilidad 24×7 con SLA mensual ≥ 99 % (≤ 7 h 18 min de caída al mes). | Monitor externo de `/health/ready` cada minuto. |
| NFR-009 | Despliegues sin interrupción: 0 errores 5xx durante un despliegue rolling. | Prueba de carga durante un despliegue. |
| NFR-010 | Tolerancia a la caída de una réplica de la API sin pérdida de servicio. | Prueba de caos: detener una réplica bajo carga. |
| NFR-011 | Backups de PostgreSQL con PITR: RPO ≤ 15 min, RTO ≤ 1 h. | Simulacro de restauración trimestral. |
| NFR-012 | Alertas cuando la disponibilidad o el p95 se degraden. | Revisión de la configuración de monitoreo. |

## Entidades clave

- **User**: ver `spec/domain/user.md`.

## Fuera de alcance (esta feature)

- Autenticación y autorización.
- Reactivación de usuarios.
- Rate limiting.
- Búsqueda o filtros adicionales en `GET /users`.

## Aclaraciones

### Sesión 2026-10-05 (decisiones propuestas, pendientes de confirmar)
- P: ¿Cómo se pagina `GET /users`? → R: `limit`/`offset`, por defecto 20, máximo 100 (ADR-0007).
- P: ¿Qué responde `DELETE` sobre un usuario ya inactivo? → R: 204, idempotente.
- P: ¿Qué caracteres admiten nombres y apellidos? → R: letras Unicode (incluye acentos y ñ), espacios, guion y apóstrofo; deben empezar con letra; se recortan espacios en los extremos.
- P: ¿`PUT` con `email` o `status` en el cuerpo? → R: 422 (el esquema no admite propiedades adicionales).
- P: ¿Existe reactivación? → R: fuera de alcance para esta feature.
- P: ¿Qué disponibilidad se exige? → R: 24×7 con SLA mensual de 99 % (confirmado por el usuario).
- P: ¿Las ventanas de mantenimiento cuentan como caída? → R: sí; por eso los despliegues y migraciones deben ser sin interrupción (propuesto).
- P: ¿Qué `code` usan los errores de rutas o métodos fuera del contrato? → R: `NOT_FOUND` (404) y `METHOD_NOT_ALLOWED` (405); `USER_NOT_FOUND` queda solo para usuarios inexistentes (2026-10-04, T010).

### Pendientes
- [NEEDS CLARIFICATION] Estrategia de autenticación (p. ej. API key o JWT/OAuth2) antes de exponer la API en producción.
- [NEEDS CLARIFICATION] Límites de rate limiting.
- [NEEDS CLARIFICATION] Proveedor cloud o plataforma de despliegue (ADR-0008 deja la elección abierta).

## Criterios de éxito

- SC-001: Todos los escenarios de aceptación tienen una prueba automatizada en verde.
- SC-002: Schemathesis no reporta ninguna violación del contrato.
- SC-003: NFR-001 y NFR-002 se cumplen en la prueba de carga.
- SC-004: El primer mes en producción cumple NFR-008 (≥ 99 % de disponibilidad).
