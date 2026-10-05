# ADR-0005 — SQLAlchemy 2.0 async + asyncpg + Alembic

## Estado

Propuesto

## Contexto

La capa de infraestructura debe implementar los contratos de repositorio del dominio (ADR-0001)
sobre PostgreSQL (ADR-0003). Las migraciones deben ser reproducibles y reversibles.

## Decisión

- **SQLAlchemy 2.0** en modo asíncrono para el acceso a datos, mapeando a entidades de dominio en el repositorio.
- **asyncpg** como driver.
- **Alembic** como herramienta de migraciones.
- Pool de conexiones: `pool_size=10`, `max_overflow=5`, `pool_timeout=5s`, `pool_pre_ping=True` (configurable por entorno).

## Alternativas consideradas

- SQLModel: acopla modelo API y modelo de persistencia.
- psycopg 3 + SQL plano: más control, más código repetitivo.
- Tortoise ORM: menor ecosistema de migraciones.

## Consecuencias

### Positivas
- Los modelos ORM quedan en `infrastructure/`; el dominio permanece puro.
- Alembic permite `upgrade`/`downgrade` en CI y en pruebas de integración.

### Negativas
- Requiere mapear entre modelo ORM y entidad de dominio.
- El modo async de SQLAlchemy exige cuidado con la carga perezosa (lazy loading).
