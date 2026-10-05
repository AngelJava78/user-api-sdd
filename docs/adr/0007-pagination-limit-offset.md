# ADR-0007 — Paginación por limit/offset en GET /users

## Estado

Propuesto

## Contexto

`GET /users` debe paginar (pendiente en `consistency-checklist.md`). El volumen es ~1 000 usuarios.

## Decisión

- Parámetros de consulta: `limit` (1–100, por defecto 20) y `offset` (≥ 0, por defecto 0).
- Orden estable: `created_at ASC, id ASC`.
- Respuesta: `{ "items": [...], "total": n, "limit": l, "offset": o }`.
- `limit` u `offset` fuera de rango → 422 con esquema `Error`.

## Alternativas consideradas

- Paginación por cursor (keyset): mejor para millones de filas o datos muy cambiantes; innecesaria a esta escala y más compleja de consumir.

## Consecuencias

- Simple de implementar y probar.
- Con 1 000 filas el coste de `OFFSET` y de `COUNT(*)` es despreciable. Si el volumen crece en órdenes de magnitud, revisar esta decisión.
