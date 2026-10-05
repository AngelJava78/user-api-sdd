# Constitución del proyecto — Users API

> La constitución define los principios **no negociables** del proyecto. Toda especificación,
> plan, tarea e implementación debe cumplirlos. Cada `plan.md` incluye un *Constitution Check*
> que verifica su cumplimiento antes de pasar a tareas.

**Versión:** 1.1.0 · **Ratificada:** 2026-10-05 · **Última enmienda:** 2026-10-05 (se añade el principio X)

## Principios

### I. La especificación es la fuente de verdad
- Ningún comportamiento se implementa sin estar descrito en `spec/` o en una feature de `features/`.
- Si el código y la especificación divergen, el error está en el código, salvo que se enmiende primero la especificación.
- Todo cambio funcional comienza modificando la especificación (requisitos → aceptación → contrato → datos).

### II. Contrato primero (Contract-First)
- `spec/openapi/users-api.yaml` es el contrato HTTP canónico.
- El contrato se escribe y revisa **antes** del código; el framework no es la fuente del contrato.
- Las pruebas de contrato verifican automáticamente que la API implementada cumple el OpenAPI.

### III. Pruebas primero (Test-First)
- Las pruebas derivadas de los criterios de aceptación se escriben antes de la implementación y deben fallar primero (rojo → verde → refactor).
- Orden obligatorio: contrato → integración → unitarias → implementación.
- Ninguna tarea de implementación se considera terminada sin sus pruebas en verde.

### IV. Dominio independiente
- Las reglas de negocio viven en `domain/` y no importan FastAPI, SQLAlchemy ni PostgreSQL.
- Las dependencias apuntan hacia el dominio (ver ADR-0001).

### V. Trazabilidad
- Cada requisito tiene un identificador (`FR-xxx`, `NFR-xxx`).
- Cada criterio de aceptación referencia su requisito; cada tarea referencia los requisitos que cubre.
- Una tarea sin requisito asociado no se ejecuta.

### VI. Simplicidad (YAGNI)
- Se implementa solo lo especificado. No se añaden capas, caché, colas ni servicios externos sin un requisito que lo justifique.
- Toda complejidad adicional se justifica en la sección *Complexity Tracking* del plan.

### VII. Seguridad y configuración
- Ningún secreto se versiona; la configuración llega por variables de entorno (`.env.example` documenta las claves).
- Toda entrada externa se valida en el borde (capa API) y las invariantes se refuerzan en dominio y base de datos.
- Las consultas SQL siempre se parametrizan.

### VIII. Observabilidad
- Logs estructurados (JSON) con `request_id` en cada petición.
- Las operaciones de escritura (crear, actualizar, desactivar) registran un evento de log.
- Endpoints de salud `live` y `ready` disponibles para el orquestador y el balanceador.

### IX. Decisiones documentadas
- Toda decisión técnica relevante se registra como ADR en `docs/adr/`.
- Las decisiones abiertas se marcan como `[NEEDS CLARIFICATION]` y se resuelven antes del plan.

### X. Disponibilidad
- La API se diseña para estar disponible 24×7 con un SLA mensual de 99 %.
- Ningún cambio puede requerir detener el servicio: despliegues rolling, apagado ordenado y migraciones expand/contract.
- El SLA se mide de forma externa y continua; las alertas avisan antes de agotar el presupuesto de caída.

## Flujo de trabajo y calidad

- Puertas de calidad obligatorias en CI: `ruff check`, `ruff format --check`, `mypy --strict`, `pytest` (cobertura mínima 90 % en `domain/` y `application/`).
- Las migraciones son reproducibles y reversibles (Alembic).
- Cada Pull Request indica qué requisitos (`FR/NFR`) cubre y enlaza la feature correspondiente.

## Gobernanza

- La constitución prevalece sobre cualquier otra guía del repositorio.
- Las enmiendas requieren: cambio documentado en este archivo, incremento de versión (SemVer) y revisión de los planes afectados.
  - MAJOR: se elimina o redefine un principio.
  - MINOR: se añade un principio o sección.
  - PATCH: aclaraciones de redacción.
