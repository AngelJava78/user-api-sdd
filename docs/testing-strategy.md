# Estrategia de pruebas

## Contract tests

Validan que la API implementa el contrato OpenAPI.

## Unit tests

Cubren:

- reglas del dominio;
- validaciones;
- casos de uso;
- comportamiento ante errores.

## Integration tests

Cubren:

- conexión con PostgreSQL;
- persistencia;
- restricciones de unicidad;
- transacciones;
- migraciones.

## Matriz mínima

| Caso | Unit | Contract | Integration |
|---|---:|---:|---:|
| Listar usuarios | Sí | Sí | Sí |
| Obtener usuario existente | Sí | Sí | Sí |
| Obtener usuario inexistente | Sí | Sí | Sí |
| Crear usuario válido | Sí | Sí | Sí |
| Crear usuario inválido | Sí | Sí | Sí |
| Crear email duplicado | Sí | Sí | Sí |
| Actualizar usuario | Sí | Sí | Sí |
| Actualizar inexistente | Sí | Sí | Sí |
| Eliminar usuario | Sí | Sí | Sí |
| Eliminar inexistente | Sí | Sí | Sí |

## Herramientas

| Tipo | Herramienta |
|---|---|
| Runner | pytest + pytest-asyncio |
| Cliente HTTP | httpx (`AsyncClient` + `ASGITransport`) |
| Contrato | Schemathesis contra `spec/openapi/users-api.yaml` |
| Integración | testcontainers-python (PostgreSQL 17) + migraciones Alembic |
| Cobertura | pytest-cov (≥ 90 % en `domain/` y `application/`) |
| Carga | Locust (200 usuarios concurrentes, 80 % lecturas / 20 % escrituras) |

## Casos adicionales

| Caso | Unit | Contract | Integration |
|---|---:|---:|---:|
| Paginación y límites de `limit`/`offset` | Sí | Sí | Sí |
| `user_id` no UUID → 422 | No | Sí | Sí |
| `PUT` con campos no permitidos → 422 | Sí | Sí | Sí |
| `DELETE` repetido → 204 | Sí | Sí | Sí |
| Dos `POST` concurrentes con el mismo email | No | No | Sí |
| Migraciones `upgrade`/`downgrade` | No | No | Sí |
| `/health/ready` con base de datos caída → 503 | No | No | Sí |
| Apagado ordenado con `SIGTERM` | No | No | Sí |

## Pruebas de carga (NFR-001, NFR-002)

- p95 < 200 ms en lecturas y < 300 ms en escrituras.
- Errores 5xx < 0,1 %.
- Se ejecutan contra un entorno con la misma configuración de workers y pool que producción.

## Pruebas de disponibilidad (NFR-008 a NFR-011)

- Locust con 200 usuarios durante un despliegue rolling: 0 errores 5xx.
- Detener una réplica bajo carga: el servicio continúa.
- Simulacro trimestral de restauración PITR: RTO ≤ 1 h.
