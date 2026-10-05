# Arquitectura

## Estilo

Arquitectura por capas con separación entre:

- API / transporte HTTP.
- Aplicación / casos de uso.
- Dominio.
- Infraestructura / persistencia.

## Dependencias

La dirección de dependencias debe apuntar hacia el dominio:

API -> Application -> Domain
Infrastructure implementa contratos utilizados por Application/Domain.

## Objetivo

Evitar que las reglas de negocio dependan directamente de PostgreSQL o del framework HTTP.

## Componentes previstos

### API
Responsable de HTTP, serialización, validación de entrada y códigos de respuesta.

### Application
Responsable de casos de uso: listar, obtener, crear, actualizar y eliminar usuarios.

### Domain
Responsable de entidades, invariantes y contratos de repositorio.

### Infrastructure
Responsable de PostgreSQL, configuración y detalles técnicos de persistencia.

## Tecnología por capa

| Capa | Tecnología | Puede depender de |
|---|---|---|
| API | FastAPI, Pydantic v2 | Application, Domain |
| Application | Python puro | Domain |
| Domain | Python puro (dataclasses) | Nada |
| Infrastructure | SQLAlchemy 2.0 async, asyncpg, Alembic, structlog | Domain |

Detalle del stack en `docs/tech-stack.md`.
