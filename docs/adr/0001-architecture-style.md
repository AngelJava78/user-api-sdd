# ADR-0001 — Arquitectura por capas

## Estado

Propuesto

## Contexto

La API necesita separar las reglas de negocio de los detalles de HTTP y PostgreSQL.

## Decisión

Usar una arquitectura por capas con API, Application, Domain e Infrastructure.

## Consecuencias

### Positivas

- Facilita pruebas unitarias.
- Reduce acoplamiento con PostgreSQL.
- Permite cambiar detalles técnicos con menor impacto.

### Negativas

- Introduce más archivos y abstracciones.
- Requiere disciplina para mantener los límites entre capas.
