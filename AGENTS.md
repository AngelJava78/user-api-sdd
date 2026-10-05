# Guía para agentes de IA (y humanos)

Este repositorio sigue **Spec-Driven Development**. Si eres un asistente de IA (Claude Code, Copilot, Cursor, etc.):

1. Lee primero `CONSTITUTION.md`. Sus principios son obligatorios.
2. Lee la especificación viva en `spec/` y la feature activa en `features/NNN-*/`.
3. No escribas código que no esté respaldado por una tarea de `tasks.md` con su requisito `FR/NFR`.
4. Si detectas ambigüedad, no la resuelvas inventando: márcala como `[NEEDS CLARIFICATION]` y pregunta.
5. Si un cambio afecta al contrato, actualiza primero `spec/openapi/users-api.yaml`.
6. Respeta el stack definido en `docs/tech-stack.md`; no añadas dependencias sin ADR.
7. Al terminar una tarea, márcala `[x]` en `tasks.md`.

Comandos de calidad (cuando exista implementación): `uv run ruff check . && uv run mypy src && uv run pytest`.
