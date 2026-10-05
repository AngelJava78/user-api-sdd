# ADR-0008 — Disponibilidad 99 % y estrategia de despliegue

## Estado

Propuesto

## Contexto

La API debe estar disponible 24×7 con un SLA mensual de 99 %. Eso deja un presupuesto de caída de
**~7 h 18 min al mes**. Las ventanas de mantenimiento cuentan como caída, así que desplegar o migrar
no puede detener el servicio. La carga es moderada (~200 concurrentes), por lo que el reto es la
disponibilidad, no la capacidad.

## Decisión

1. **API:** mínimo **2 réplicas** en contenedores, sin estado, detrás de un balanceador con health checks.
   - `GET /health/live`: el orquestador reinicia la réplica si falla.
   - `GET /health/ready`: el balanceador saca la réplica del tráfico si PostgreSQL no responde.
2. **Despliegue rolling** (o blue/green): una réplica nueva solo recibe tráfico cuando `/health/ready` responde 200.
3. **Apagado ordenado:** al recibir `SIGTERM`, la réplica deja de estar *ready*, termina las peticiones en curso
   (hasta `SHUTDOWN_GRACE_SECONDS`) y cierra el pool de conexiones.
4. **PostgreSQL gestionado** (p. ej. AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL) con backups automáticos y PITR.
   Alta disponibilidad multi-zona recomendada pero opcional: un 99 % no la exige estrictamente, aunque reduce el RTO.
5. **Migraciones expand/contract** ejecutadas como paso previo al despliegue, nunca al arrancar cada réplica.
6. **Observabilidad:** monitor externo de `/health/ready` cada minuto, métricas de latencia y errores, y alertas
   cuando se consuma el 50 % del presupuesto de caída del mes.
7. **Plataforma:** contenedores en un servicio gestionado (p. ej. AWS ECS Fargate, Google Cloud Run, Azure Container Apps,
   Railway, Render o Kubernetes gestionado). La elección concreta queda pendiente (`[NEEDS CLARIFICATION]`).

## Alternativas consideradas

- **Una sola instancia con reinicio automático:** podría llegar a 99 %, pero cada despliegue y cada fallo provocan caída. Descartado.
- **Multi-región activo-activo:** necesario para 99,99 %, pero excesivo y caro para 99 %. Descartado.
- **PostgreSQL autogestionado en una VM:** backups, parches y failover quedan a cargo del equipo. Descartado para una startup.

## Consecuencias

### Positivas
- Despliegues y caídas de una réplica no consumen presupuesto de SLA.
- La operación de la base de datos queda en manos del proveedor.

### Negativas
- Coste de al menos 2 réplicas y una base de datos gestionada.
- Las migraciones exigen disciplina (expand/contract).
- El SLA del proveedor de la base de datos también limita el SLA total; debe ser ≥ 99,9 %.
