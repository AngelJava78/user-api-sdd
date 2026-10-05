# Especificación de dominio — User

## Identidad

El usuario se identifica mediante un UUID.

## Atributos

- `id`: identificador único.
- `email`: correo electrónico único e inmutable.
- `name`: nombre del usuario. Obligatorio, máximo 30 caracteres.
- `lastname`: apellido paterno. Obligatorio, máximo 30 caracteres.
- `second_lastname`: apellido materno. Opcional, máximo 30 caracteres.
- `status`: estado del usuario. `true` = activo, `false` = inactivo.
- `created_at`: fecha de creación.
- `updated_at`: fecha de última modificación.

## Invariantes

- `id` no puede repetirse.
- `email` no puede repetirse.
- La unicidad de `email` no distingue mayúsculas/minúsculas.
- `email` debe tener formato válido.
- `email` no puede modificarse mediante `PUT`.
- `name` debe cumplir las restricciones de longitud y validación de dominio.
- `lastname` debe cumplir las restricciones de longitud y validación de dominio.
- `second_lastname`, cuando se proporciona, debe cumplir las restricciones de longitud y validación de dominio.
- Las fechas son gestionadas por el sistema.
- `status` solo puede ser modificado por las operaciones de activación/desactivación definidas por la API; `PUT` no modifica `status`.

## Comportamiento

### Crear

Debe rechazar datos inválidos y correos duplicados. Un usuario creado inicia como activo (`status = true`).

### Consultar

Un usuario activo puede consultarse normalmente. Los usuarios inactivos se conservan y pueden consultarse mediante su identificador.

### Actualizar

`PUT` mantiene la identidad, el email y el status del usuario. Solo actualiza los campos modificables definidos por el contrato.

### Eliminar

La operación `DELETE` no elimina físicamente el registro. Desactiva el usuario estableciendo `status = false`. Desactivar un usuario ya inactivo no produce error ni cambios (idempotente).

## Reglas de validación de nombres

Aplican a `name`, `lastname` y `second_lastname`:

- Se recortan los espacios en los extremos antes de validar.
- Longitud entre 1 y 30 caracteres tras el recorte.
- Caracteres permitidos: letras Unicode (incluye acentos, diéresis y ñ), espacio, guion (`-`) y apóstrofo (`'`).
- Debe comenzar con una letra.
- `second_lastname` vacío tras el recorte se trata como `null`.

## Normalización de email

- Se recortan los espacios en los extremos y se convierte a minúsculas antes de validar y persistir.
- Longitud máxima 320 caracteres.

## Decisiones pendientes

- Reactivación de usuarios: fuera de alcance de la versión 1.
