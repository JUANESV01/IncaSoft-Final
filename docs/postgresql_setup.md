# Configuracion de PostgreSQL para INCASOFT Solutions

Esta configuracion esta pensada para desarrollo local en Windows.

## Version recomendada

Instala PostgreSQL 18.3.3 de 64 bits.

## Parametros de instalacion

- Puerto: `5432`
- Locale: `Spanish_Colombia.1252`
- Superusuario local: `postgres`
- Base de datos de la app: `incasoft_db`
- Usuario de la app: `incasoft_user`
- Password: `IncaSoft2026_DB!`

## SQL inicial

Ejecutar en pgAdmin4 con el usuario `postgres`:

```sql
CREATE DATABASE incasoft_db
  WITH ENCODING 'UTF8'
  TEMPLATE template0;

CREATE USER incasoft_user WITH PASSWORD 'IncaSoft2026_DB!';

ALTER ROLE incasoft_user SET client_encoding TO 'utf8';
ALTER ROLE incasoft_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE incasoft_user SET timezone TO 'America/Bogota';

GRANT ALL PRIVILEGES ON DATABASE incasoft_db TO incasoft_user;

\c incasoft_db
GRANT ALL ON SCHEMA public TO incasoft_user;
ALTER SCHEMA public OWNER TO incasoft_user;
```

## postgresql.conf recomendado

Para un equipo local con 8 GB de RAM:

```conf
listen_addresses = 'localhost'
port = 5432
max_connections = 50
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 8MB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
timezone = 'America/Bogota'
log_min_duration_statement = 500ms
```

```env
DB_ENGINE=postgresql
DB_NAME=incasoft_db
DB_USER=incasoft_user
DB_PASSWORD=IncaSoft2026_DB!
DB_HOST=127.0.0.1
DB_PORT=5432
DB_CONN_MAX_AGE=60
DB_CONN_HEALTH_CHECKS=True
DB_CONNECT_TIMEOUT=10
DB_APPLICATION_NAME=incasoft_solutions
DB_SSLMODE=prefer
DB_SESSION_OPTIONS=-c timezone=America/Bogota
```

## Migracion de la app

Con PostgreSQL instalado y el archivo `.env` creado:

```powershell
python.exe manage.py migrate
python.exe manage.py seed_demo
python.exe manage.py runserver
```
