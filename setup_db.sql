-- Script para crear la base de datos y usuario de INCASOFT en PostgreSQL 18
-- Ejecutar como superusuario (postgres):
--   /Library/PostgreSQL/18/bin/psql -U postgres -h 127.0.0.1 -f setup_db.sql

-- 1. Crear usuario
CREATE USER incasoft_user WITH PASSWORD 'incasoft_pass';

-- 2. Crear base de datos
CREATE DATABASE incasoft_db
    OWNER = incasoft_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'es_CO.UTF-8'
    LC_CTYPE = 'es_CO.UTF-8'
    TEMPLATE = template0;

-- 3. Permisos
GRANT ALL PRIVILEGES ON DATABASE incasoft_db TO incasoft_user;
