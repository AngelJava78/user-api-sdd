---
description: Implementa una tarea de features/001-users-crud/tasks.md siguiendo SDD
argument-hint: ID de la tarea, por ejemplo T015
---

Vas a ejecutar la tarea $ARGUMENTS de `features/001-users-crud/tasks.md`.

1. Lee la tarea y los requisitos (FR/NFR) que menciona en `features/001-users-crud/spec.md`, y las partes relevantes de `plan.md`, `spec/` y el contrato OpenAPI.
2. Comprueba que las tareas de las que depende estén marcadas como hechas. Si no, avísame y detente.
3. Explícame en pocas líneas qué archivos vas a crear o cambiar y espera mi confirmación.
4. Si es una tarea de pruebas: escribe las pruebas, ejecútalas y muéstrame que fallan.
   Si es de implementación: implementa lo mínimo para que pasen las pruebas existentes.
5. Ejecuta `uv run ruff check . && uv run mypy src && uv run pytest` (lo que ya exista) y muéstrame el resultado.
6. Marca la tarea como `[x]` en `tasks.md` y resume qué hiciste. No empieces la siguiente tarea.
