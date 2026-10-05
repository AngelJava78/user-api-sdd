# Criterios de aceptación

## GET /users

- Devuelve HTTP 200 cuando la consulta es válida.
- Devuelve una colección con el esquema definido.
- Devuelve únicamente usuarios con `status = true`.
- Acepta `limit` (1–100, por defecto 20) y `offset` (≥ 0, por defecto 0).
- Devuelve `items`, `total`, `limit` y `offset`; orden `created_at, id` ascendente.
- `limit` u `offset` fuera de rango devuelven HTTP 422.

## GET /users/{user_id}

- Devuelve HTTP 200 si el usuario existe.
- Devuelve HTTP 404 si no existe.
- Devuelve HTTP 422 si `user_id` no es un UUID válido.
- Puede devolver usuarios activos e inactivos.
- El cuerpo debe coincidir con `User`.

## POST /users

- Devuelve HTTP 201 al crear correctamente.
- Debe validar el payload.
- Debe rechazar un email duplicado con HTTP 409, sin distinguir mayúsculas/minúsculas.
- El email se almacena normalizado: sin espacios en los extremos y en minúsculas.
- Dos creaciones concurrentes con el mismo email producen un 201 y un 409.
- El usuario creado debe iniciar con `status = true`.
- Debe devolver el recurso creado conforme al contrato.

## PUT /users/{user_id}

- Devuelve HTTP 200 al actualizar correctamente.
- Devuelve HTTP 404 si el usuario no existe.
- Debe validar el payload.
- No permite modificar `id`, `email` ni `status`: enviarlos devuelve HTTP 422.
- Actualiza `updated_at`.
- Debe rechazar conflictos de unicidad si una futura modificación del contrato permite campos únicos adicionales.

## DELETE /users/{user_id}

- Devuelve HTTP 204 cuando desactiva correctamente.
- Devuelve HTTP 404 si el usuario no existe.
- No elimina físicamente el registro.
- La operación establece `status = false`.
- Repetir DELETE sobre un usuario ya inactivo devuelve HTTP 204 sin cambios (idempotente).

## Errores

Los errores deben utilizar el esquema `Error` definido en OpenAPI con códigos estables: `VALIDATION_ERROR` (422), `USER_NOT_FOUND` (404), `EMAIL_ALREADY_EXISTS` (409), `SERVICE_UNAVAILABLE` (503), `INTERNAL_ERROR` (500), `NOT_FOUND` (404, ruta inexistente) y `METHOD_NOT_ALLOWED` (405, método no soportado).

Las operaciones de `/users` rechazan los parámetros de consulta no declarados en el contrato con HTTP 422 `VALIDATION_ERROR` y el nombre del parámetro en `details`. Las sondas `/health/*` los ignoran (p. ej. parámetros anti-caché de monitores).

## GET /health/live

- Devuelve HTTP 200 con `{"status": "ok"}` mientras el proceso esté en ejecución.
- No consulta la base de datos.

## GET /health/ready

- Devuelve HTTP 200 con `{"status": "ok"}` si la base de datos responde.
- Devuelve HTTP 503 `SERVICE_UNAVAILABLE` si la base de datos no está disponible o la instancia se está apagando.

## Disponibilidad

- Un despliegue de una nueva versión no produce respuestas 5xx ni conexiones rechazadas (despliegue rolling + apagado ordenado).
- La caída de una réplica de la API no interrumpe el servicio.
- La disponibilidad mensual medida por el monitor externo es ≥ 99 %.
