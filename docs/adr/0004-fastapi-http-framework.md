# ADR-0004 — FastAPI como framework HTTP

## Estado

Propuesto

## Contexto

La API es CRUD, I/O-bound, con 100–200 usuarios concurrentes. Se sigue un enfoque contract-first
(ADR-0002) y se necesita validación estricta de entrada.

## Decisión

Usar **FastAPI** con **Pydantic v2**, servido por **Uvicorn** con 2–4 workers.

El OpenAPI que FastAPI genera **no** reemplaza al contrato canónico (`spec/openapi/users-api.yaml`):
las pruebas de contrato (Schemathesis) verifican que la app cumple el contrato escrito a mano.

## Alternativas consideradas

Comparativa detallada con fuentes: `docs/research/drf-vs-fastapi.md`.


- Django REST Framework: más pesado y síncrono por defecto.
- Flask: sin async ni OpenAPI integrados.
- Litestar: técnicamente sólido, menor comunidad.

## Consecuencias

### Positivas
- Async nativo, buen rendimiento para la carga prevista.
- Validación y serialización declarativas.
- Documentación interactiva (`/docs`) útil durante el desarrollo.

### Negativas
- Riesgo de deriva entre el OpenAPI generado y el canónico; se mitiga con pruebas de contrato en CI.
- La validación de FastAPI devuelve 422 con su propio formato; se debe adaptar al esquema `Error` del contrato.
