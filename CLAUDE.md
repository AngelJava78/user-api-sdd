# CLAUDE.md

Este proyecto sigue Spec-Driven Development. Antes de cualquier cambio, lee y respeta:

@CONSTITUTION.md
@AGENTS.md

## Contexto rápido

- Especificación viva: `spec/` (el contrato canónico es `spec/openapi/users-api.yaml`).
- Feature activa: `features/001-users-crud/` (`spec.md` → `plan.md` → `tasks.md`).
- Stack: `docs/tech-stack.md`. No añadas dependencias que no estén ahí sin proponer un ADR.

## Forma de trabajar

- Trabaja **una tarea de `tasks.md` a la vez** y detente al terminarla para que la revise.
- En tareas de prueba: escribe la prueba, ejecútala y muestra que **falla** antes de implementar.
- En tareas de implementación: haz pasar las pruebas y ejecuta `uv run ruff check . && uv run mypy src && uv run pytest`.
- Si la spec es ambigua o contradice el código, **pregunta**; no inventes comportamiento.
- Responde en español.
