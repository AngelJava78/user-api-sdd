# Guía paso a paso: de la especificación al código con Claude Code

Esta guía es para ti si es tu primera vez con **Spec-Driven Development (SDD)** y con **Claude Code**.
La idea central de SDD es simple: **tú decides el qué (la spec), Claude escribe el cómo (el código), y las pruebas comprueban que el código cumple la spec.** Tu trabajo principal deja de ser teclear código y pasa a ser revisar.

---

## Paso 0 — Entiende qué tienes en el proyecto

| Archivo | Para qué sirve | ¿Quién lo lee? |
|---|---|---|
| `CONSTITUTION.md` | Las reglas que nunca se rompen (pruebas primero, la spec manda…) | Tú y Claude |
| `spec/` | Cómo debe comportarse la API (requisitos, contrato OpenAPI, datos) | Tú y Claude |
| `features/001-users-crud/spec.md` | Qué construimos ahora: historias, requisitos FR/NFR | Tú y Claude |
| `features/001-users-crud/plan.md` | Cómo lo construimos: stack y estructura de carpetas | Claude, sobre todo |
| `features/001-users-crud/tasks.md` | La lista de 47 tareas en orden. **Es tu hoja de ruta.** | Tú y Claude |
| `CLAUDE.md` | Instrucciones que Claude Code lee automáticamente al abrir el proyecto | Claude |
| `.claude/commands/tarea.md` | Un comando `/tarea T0xx` para ejecutar una tarea con el flujo SDD | Claude |

---

## Paso 1 — Instala lo necesario

1. **Git**: https://git-scm.com/downloads
2. **Docker Desktop** (para PostgreSQL y las pruebas de integración): https://www.docker.com/products/docker-desktop/
3. **uv** (gestor de Python; también instala Python 3.13 por ti): https://docs.astral.sh/uv/getting-started/installation/
4. **Claude Code**:
   - En VS Code abre la vista de extensiones (`Ctrl+Shift+X` / `Cmd+Shift+X`), busca **"Claude Code"** (publicada por Anthropic) e instálala.
   - Ábrela con el icono **Spark** (✱) de la barra superior del editor (aparece con un archivo abierto) o de la barra lateral izquierda.
   - Inicia sesión con tu cuenta de Claude cuando te lo pida (necesitas un plan de pago de Claude o una cuenta de Console).
   - Documentación oficial: https://code.claude.com/docs/en/vs-code
5. Comprueba en la terminal de VS Code (`Ctrl+ñ` o *Terminal → New Terminal*):
   ```bash
   git --version
   docker --version
   uv --version
   ```

## Paso 2 — Prepara el repositorio

En la terminal, dentro de la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Especificación inicial SDD"
```

**¿Por qué?** Git es tu red de seguridad. Harás un commit después de cada tarea; si Claude hace algo que no te gusta, vuelves atrás con `git restore .` (descarta los cambios que aún no confirmaste).

## Paso 3 — Cierra las decisiones pendientes (todavía sin código)

SDD dice: **no se programa sobre decisiones abiertas.** Antes de empezar:

1. Lee los ADR `docs/adr/0004` a `0008`. Si estás de acuerdo, cambia su estado de `Propuesto` a `Aceptado`.
2. Revisa la sección *Aclaraciones* de `features/001-users-crud/spec.md` y confirma o cambia las decisiones propuestas.
3. La autenticación, el rate limiting y la plataforma de despliegue pueden quedar pendientes: no bloquean las primeras fases.

Puedes pedirle ayuda a Claude para esto. Abre el panel de Claude Code (icono Spark) y escribe:

> Lee `CONSTITUTION.md`, `spec/` y `features/001-users-crud/`. No escribas código. Dime si encuentras contradicciones entre los documentos o requisitos ambiguos.

Corrige en la spec lo que te señale. **Ese es el ciclo SDD: el problema se arregla en la spec, no en el código.**

## Paso 4 — Aprende 5 cosas de Claude Code

| Qué | Cómo | Para qué |
|---|---|---|
| **Modo de permisos** | Indicador de modo debajo de la caja de texto | Al principio elige **Manual**: Claude te pide permiso antes de cada edición o comando, y así aprendes qué hace. |
| **Modo plan** | Escribe `/plan` o elígelo en el indicador de modo | Claude investiga y propone sin tocar archivos. Úsalo cuando no tengas claro cómo abordar una tarea. |
| **Conversación nueva** | Botón de nueva conversación o `/clear` | Empieza limpio entre tareas: el contexto está en los archivos, no en el chat. |
| **Mencionar archivos** | Escribe `@` y el nombre del archivo | Le das contexto exacto: `@features/001-users-crud/tasks.md`. |
| **`/tarea T0xx`** | Comando incluido en este proyecto (`.claude/commands/tarea.md`) | Ejecuta una tarea con el flujo SDD completo. Si no aparece al escribir `/`, abre ese archivo, copia su texto en el chat y cambia `$ARGUMENTS` por el ID de la tarea. |

## Paso 5 — El ciclo de cada tarea (repítelo 47 veces)

```text
 1. Conversación nueva (o /clear)
 2. /tarea T0xx                 ← Claude lee la tarea y la spec
 3. Claude te dice qué hará     ← lee y confirma (o corrige)
 4. Claude escribe y ejecuta    ← apruebas los cambios
 5. Revisas el resultado:
      ¿Es una prueba?           → debe FALLAR (aún no hay código)
      ¿Es implementación?       → las pruebas deben PASAR
 6. git add . && git commit -m "T0xx: descripción"
```

**Regla de oro:** si en el paso 5 descubres que la spec estaba mal o incompleta, **detente**, corrige primero la spec (`spec/` o `features/001-users-crud/spec.md`) y después pide a Claude que ajuste el código.

## Paso 6 — Tu recorrido por fases

### Fase 1 — Preparación (T001–T005)
Crea el proyecto Python, las herramientas de calidad y Docker.

> /tarea T001

Al terminar, comprueba tú mismo:
```bash
uv run python --version     # 3.13.x
docker compose -f infra/docker-compose.yml up -d db
```

### Fase 2 — Fundamentos (T006–T014)
Base de datos, migraciones, manejo de errores, logs, salud. Aquí verás por primera vez una prueba **en rojo** que luego pasa a **verde**.

> /tarea T008

Fíjate en que Claude escriba la prueba de migraciones **antes** de que la migración exista (T008 depende de T007, así que ve en orden).

### Fase 3 — Primera historia: registrar usuario (T015–T023) 🎯
Esta es tu primera funcionalidad real. Primero las pruebas (T015–T019), todas en rojo; después la implementación (T020–T023), que las pone en verde.

Al terminar T023 prueba la API a mano:
```bash
uv run uvicorn app.main:app --reload
```
Abre http://localhost:8000/docs y crea un usuario. Compara lo que ves con los escenarios de **US-1** en `spec.md`.

### Fases 4 a 6 — Consultar, actualizar y desactivar (T024–T035)
Mismo ciclo. Ya conoces el ritmo.

### Fase 7 — Validación (T036–T040)
Pruebas de contrato (¿la API cumple el OpenAPI?), de carga y de cobertura. Ejecuta `features/001-users-crud/quickstart.md` paso a paso.

### Fase 8 — Disponibilidad (T041–T047)
Para esta fase necesitas haber elegido plataforma de despliegue.

## Paso 7 — Qué revisar en cada cambio de Claude

- ¿El cambio corresponde a **la tarea pedida**, y solo a esa?
- ¿Las pruebas nombran el requisito que cubren (`FR-004`, etc.)?
- ¿`domain/` sigue sin importar FastAPI ni SQLAlchemy? (Principio IV)
- ¿Añadió alguna dependencia que no está en `docs/tech-stack.md`? Si es así, pregúntale por qué.
- ¿Las pruebas pasan cuando las ejecutas **tú** en la terminal (`uv run pytest`)?

## Prompts útiles

| Situación | Prompt |
|---|---|
| No entiendes algo | "Explícame qué hace `@src/app/domain/user.py` como si fuera mi primera vez con Python." |
| Ver el avance | "Lee `@features/001-users-crud/tasks.md` y dime qué tareas faltan y cuál sigue." |
| Una prueba falla | "La prueba X falla con este error: … Diagnostica la causa sin cambiar la spec." |
| Quieres cambiar el comportamiento | "Quiero que <cambio>. Primero actualiza `spec/` y `features/001-users-crud/spec.md`, muéstramelo y espera mi aprobación antes de tocar código." |
| Verificar coherencia | "Compara la implementación con `spec/openapi/users-api.yaml` y lista diferencias." |

## Errores típicos de principiante

1. **Pedir todo de golpe** ("implementa la API completa"). Pierdes el control y la trazabilidad. Ve tarea por tarea.
2. **Aceptar cambios sin leerlos.** Eres el revisor; ese es tu papel en SDD.
3. **Corregir el código y olvidar la spec.** La próxima vez Claude seguirá la spec vieja.
4. **Saltarse el "rojo".** Si una prueba nueva pasa sin código, la prueba no está probando nada.
5. **Conversaciones eternas.** Usa `/clear` entre tareas; el contexto está en los archivos, no en el chat.
