# Comparativa: Django REST Framework vs FastAPI

**Fecha:** 2026-10-05 · **Relacionado:** ADR-0004, `docs/tech-stack.md`

**Contexto del proyecto:** startup (el desarrollo tiene que ser rápido), ~1 000 usuarios registrados,
~200 concurrentes, llamadas asíncronas para responder más rápido, PostgreSQL con un ORM o capa de datos sencilla.

## Tabla comparativa

| Aspecto | Django REST Framework (DRF) | FastAPI | Mejor para tu caso |
|---|---|---|---|
| **Soporte async** | DRF **no** tiene async nativo y sus mantenedores dicen que no está previsto: *"There are no plans for REST framework to add async support"* [5]. Para async hay que usar el paquete de terceros **adrf** [6]. | Async nativo: los endpoints se declaran con `async def`. Las funciones `def` normales se ejecutan en un threadpool para no bloquear el servidor [8]. | **FastAPI** |
| **Async en el ORM** | Django tiene variantes async de los métodos del ORM (`aget`, `acreate`, `async for`), pero *"Transactions do not yet work in async mode"*; para usar transacciones hay que envolver el código con `sync_to_async()` [2]. | FastAPI no trae ORM. Usa SQLAlchemy 2.0 con `AsyncSession` sobre asyncpg o psycopg, que soporta transacciones async completas [11]. | **FastAPI** |
| **ORM / capa de datos** | ORM de Django integrado y muy maduro; no hay que elegir nada [3]. | FastAPI *"doesn't force you to use anything"*. La documentación propone SQLModel (basado en SQLAlchemy y Pydantic) [10]. | **DRF**: viene listo para usar |
| **Migraciones** | Integradas (`makemigrations` / `migrate`) [3]. | Externas: la documentación de FastAPI recomienda Alembic [10]. | **DRF** |
| **Conexión a PostgreSQL** | Driver psycopg 3 (recomendado) y pool de conexiones nativo con `OPTIONS: {"pool": True}` [4]. | Driver asyncpg o psycopg vía SQLAlchemy, con pool configurable [11]. | Empate |
| **Velocidad de desarrollo de un CRUD** | Muy alta: con `ModelSerializer`, `ViewSet` y `Router` sale un CRUD completo con muy poco código; trae además una *Browsable API* [1]. | Alta: modelos Pydantic y tipos de Python, sin sintaxis nueva [7]. Hay que ensamblar ORM, migraciones y estructura uno mismo. | **DRF** |
| **Panel de administración** | Django Admin incluido, útil para operar usuarios desde el primer día [12]. | No incluido. | **DRF** |
| **Validación de datos** | Serializers de DRF [1]. | Pydantic con tipos de Python, que valida longitudes, emails, UUID, etc. [7]. | **FastAPI**: encaja 1:1 con el contrato |
| **OpenAPI / documentación** | El generador de OpenAPI integrado está **deprecado**; DRF recomienda **drf-spectacular** [9]. | OpenAPI y JSON Schema automáticos, con Swagger UI y ReDoc incluidos [7]. | **FastAPI**: encaja con el enfoque contract-first |
| **Autenticación, permisos, throttling** | Incluidos: autenticación, permisos, throttling, paginación y filtros [1]. | Utilidades de seguridad OpenAPI (OAuth2 con JWT, API keys, HTTP Basic) [7]. El rate limiting y los permisos finos se implementan aparte. | **DRF** |
| **Rendimiento** | Bueno para apps síncronas; el stack async completo requiere ASGI y middleware async de extremo a extremo [2]. | Construido sobre Starlette, *"one of the fastest Python frameworks available"* [7]. | **FastAPI** |
| **Escalado con workers** | Gunicorn/Uvicorn con varios workers; bajo ASGI hay que desactivar las conexiones persistentes y usar pool [4]. | `fastapi run --workers 4` o `uvicorn --workers` para aprovechar varios núcleos [13]. | Empate |
| **Popularidad y tendencia** | Django: 35 % de los desarrolladores Python (2024) [14]. | FastAPI: 38 % en 2024, frente a 21 % en 2021 [14]. | Empate (ambos muy adoptados) |
| **Madurez del ecosistema** | Más de 15 años de ecosistema Django; lo usan Mozilla, Red Hat y Eventbrite [1]. | Más joven, con crecimiento rápido; base de código 100 % tipada y 100 % cubierta por tests [7]. | **DRF** |

## Qué significa para 1 000 usuarios y 200 concurrentes

Ambos frameworks soportan esta carga sin problemas con 2–4 workers y un pool de conexiones a PostgreSQL.
La carga no decide la elección; la deciden el requisito de **llamadas asíncronas** y el enfoque **contract-first**.

## Recomendación

**FastAPI**, que es lo que ya propone ADR-0004, por tres motivos:

1. **Async es un requisito tuyo.** En DRF el async no es oficial y depende de un paquete de terceros [5][6]. Además, el ORM de Django todavía no admite transacciones async [2].
2. **Contract-first.** Pydantic y el OpenAPI automático encajan directamente con `spec/openapi/users-api.yaml`. En DRF el OpenAPI integrado está deprecado [9].
3. **El alcance es pequeño.** Una API de un solo recurso no aprovecha el admin ni las "baterías incluidas" de Django, que son su gran ventaja.

**Qué cuesta elegir FastAPI:** hay que montar uno mismo el ORM (SQLAlchemy), las migraciones (Alembic), el rate limiting
y los permisos. El plan de `features/001-users-crud/` ya incluye esas piezas.

**Cuándo elegiría DRF:** si necesitaras un panel de administración desde el primer día, muchos modelos relacionados o
autenticación con permisos complejos lista para usar, y el async dejara de ser un requisito.

## Fuentes

1. Django REST Framework — página oficial: https://www.django-rest-framework.org/
2. Django — Asynchronous support: https://docs.djangoproject.com/en/stable/topics/async/
3. Django — Models and migrations: https://docs.djangoproject.com/en/stable/topics/db/models/ · https://docs.djangoproject.com/en/stable/topics/migrations/
4. Django — Databases (PostgreSQL, connection pool): https://docs.djangoproject.com/en/stable/ref/databases/
5. DRF — Discussion #7774 "Async view support" (postura de los mantenedores): https://github.com/encode/django-rest-framework/discussions/7774
6. adrf — Async Django REST framework (terceros): https://github.com/em1208/adrf
7. FastAPI — Features: https://fastapi.tiangolo.com/features/
8. FastAPI — Concurrency and async/await: https://fastapi.tiangolo.com/async/
9. DRF — Schemas (deprecación del OpenAPI integrado): https://www.django-rest-framework.org/api-guide/schemas/
10. FastAPI — SQL (Relational) Databases: https://fastapi.tiangolo.com/tutorial/sql-databases/
11. SQLAlchemy 2.0 — Asynchronous I/O (asyncio): https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
12. Django — The admin site: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
13. FastAPI — Server Workers: https://fastapi.tiangolo.com/deployment/server-workers/
14. JetBrains — Python Developers Survey 2024: https://lp.jetbrains.com/python-developers-survey-2024/
