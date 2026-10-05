# Especificación de persistencia

## Tabla: users

Diseño lógico:

| Campo | Tipo lógico | Obligatorio | Restricciones |
|---|---|---:|---|
| id | UUID | Sí | PK, generado por la aplicación (v4) |
| email | VARCHAR(320) | Sí | UNIQUE, case-insensitive |
| name | VARCHAR(30) | Sí | Validación de dominio |
| lastname | VARCHAR(30) | Sí | Apellido paterno, validación de dominio |
| second_lastname | VARCHAR(30) | No | Apellido materno, validación de dominio |
| status | BOOLEAN | Sí | `true` = ACTIVE, `false` = INACTIVE |
| created_at | TIMESTAMPTZ (UTC) | Sí | Generado por sistema |
| updated_at | TIMESTAMPTZ (UTC) | Sí | Actualizado por sistema |

## Índices y restricciones

- Primary key sobre `id`.
- Índice único `ux_users_email_lower` sobre `lower(email)` (unicidad case-insensitive, segura ante concurrencia).
- Índice `ix_users_status_created_at` sobre `(status, created_at, id)` para el listado paginado de activos.
- `status` con valor por defecto `true`.
- `status` no acepta NULL.
- `second_lastname` puede ser NULL.

## Comportamiento de eliminación

No se realiza borrado físico mediante la API. `DELETE /users/{user_id}` establece `status = false`.

Los usuarios inactivos se conservan en la base de datos.

## Migraciones

Las migraciones deben:

1. Crear la tabla.
2. Crear restricciones.
3. Crear índices.
4. Garantizar la unicidad case-insensitive de `email`.
5. Poder ejecutarse en una base vacía.
6. Poder revertirse cuando la herramienta de migraciones lo permita.

Herramienta: **Alembic** (ADR-0005). Cada migración debe tener `upgrade` y `downgrade`.

### Migraciones sin interrupción (NFR-009)

Para cumplir el SLA de 99 % las migraciones siguen el patrón **expand/contract**:

1. *Expand*: solo cambios compatibles con la versión anterior del código (añadir columnas nulables, tablas o índices con `CREATE INDEX CONCURRENTLY`).
2. Desplegar el código nuevo.
3. *Contract*: eliminar lo obsoleto en una migración posterior.

Prohibido en una sola migración: renombrar o borrar columnas en uso, o bloquear la tabla durante mucho tiempo.

## Backups (NFR-011)

- Backups automáticos diarios y PITR (WAL) gestionados por el proveedor.
- Retención mínima de 7 días.
- Restauración probada al menos una vez por trimestre.
