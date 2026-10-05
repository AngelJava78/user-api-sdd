# ADR-0003 — PostgreSQL como persistencia

## Estado

Aceptado

## Contexto

La API necesita persistencia relacional y restricciones de unicidad.

## Decisión

PostgreSQL será la base de datos principal.

## Consecuencias

- El modelo de persistencia debe expresarse mediante migraciones.
- La restricción UNIQUE de email debe existir también en la base de datos.
- Las pruebas de integración deben ejecutarse contra PostgreSQL.
