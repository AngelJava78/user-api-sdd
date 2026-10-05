# infra/

Infraestructura local de la API (T003, NFR-003).

- `docker-compose.yml`: servicios `api` y `db` (PostgreSQL 17).
- `Dockerfile`: imagen de la API (Python 3.13 + uv), sin estado y con usuario no privilegiado.

## Uso

1. Copiar `.env.example` a `.env` y completar `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   y `DATABASE_URL` (desde el host apunta a `localhost:${POSTGRES_PORT}`, por defecto 5432).
2. Desde la raíz del repositorio:

   ```sh
   # Solo la base de datos (desarrollo y pruebas desde el host)
   docker compose --env-file .env -f infra/docker-compose.yml up -d db

   # API + base de datos
   docker compose --env-file .env -f infra/docker-compose.yml up -d --build
   ```

Dentro de Compose, el servicio `api` usa `db:5432` como host de la base de datos.
