#!/usr/bin/env bash
set -e

echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

echo "==> Iniciando Gunicorn..."
exec gunicorn incasoft.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
