# Flujo de trabajo Spec-Driven Development

## Dos niveles de especificación

| Carpeta | Qué contiene | Ciclo de vida |
|---|---|---|
| `spec/` | **Especificación viva** del sistema: requisitos, dominio, contrato OpenAPI, datos, aceptación. Describe cómo es el sistema **hoy**. | Se actualiza al cerrar cada feature. |
| `features/NNN-nombre/` | **Especificación de cambio**: una feature concreta con su spec, plan y tareas. | Se crea por feature y queda como historial. |
| `CONSTITUTION.md` | Principios no negociables. | Cambia rara vez, con versión. |
| `docs/adr/` | Decisiones técnicas con su contexto. | Una por decisión; no se editan, se reemplazan. |

## Ciclo por feature

```text
 1. Constitución   → ¿la feature respeta los principios?
 2. Specify        → features/NNN/spec.md        (qué y por qué; sin tecnología)
 3. Clarify        → sección "Aclaraciones"      (resolver [NEEDS CLARIFICATION])
 4. Checklist      → features/NNN/checklists/    (calidad de la especificación)
 5. Plan           → features/NNN/plan.md + research.md (cómo; stack, estructura, Constitution Check)
 6. Contratos      → spec/openapi, spec/data     (actualizar especificación viva)
 7. Tasks          → features/NNN/tasks.md       (tareas test-first trazables a FR/NFR)
 8. Implement      → src/ y tests/               (una tarea cada vez, rojo → verde → refactor)
 9. Verify         → pruebas + quickstart.md + consistency-checklist.md
10. Cerrar         → ADRs a "Aceptado", spec viva al día, PR enlazando la feature
```

Regla de oro: **si hay que cambiar el comportamiento, se vuelve al paso 2**, nunca se corrige solo el código.

## Convenciones

- Features numeradas con tres dígitos: `001-users-crud`, `002-auth`, …
- Rama de git con el mismo nombre que la carpeta de la feature.
- Identificadores: `US-n` historias, `FR-nnn` funcionales, `NFR-nnn` no funcionales, `SC-nnn` criterios de éxito, `Tnnn` tareas, `R-nn` decisiones de investigación.
- Ambigüedades: `[NEEDS CLARIFICATION] pregunta`.
- Plantillas en `docs/sdd/templates/`.

## Compatibilidad con herramientas

Esta estructura sigue los conceptos de GitHub Spec Kit (constitution → specify → plan → tasks → implement).
Si en el futuro se usa Spec Kit u otra herramienta, basta con mapear `features/` a la carpeta que la herramienta espere.
