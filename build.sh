#!/usr/bin/env bash
# =============================================================================
# Build para Render.com (o CI)
# =============================================================================
# Este script:
#   1) Instala TODO lo declarado en requirements.txt (Django, psycopg, Gemini, etc.)
#   2) Ejecuta collectstatic para servir CSS/JS/logo con WhiteNoise
#
# NOTA: `collectstatic` puede completarse en Render aunque aún no haya SECRET_KEY en Environment
# (settings lo permite solo para ese comando). El comando **release** (`migrate`) y Gunicorn
# SÍ exigen DJANGO_SECRET_KEY o SECRET_KEY — defínalas en el panel antes de que el deploy quede Live.
# NO hace:
#   - No borra ni recrea la base de datos; los datos existentes en PostgreSQL se conservan.
#   - No ejecuta migraciones aquí (las hace Render con el comando "release" del Procfile).
#   - No crea usuarios (eso es: Render Shell → python crear_admin.py o seed_demo).
#
# Variables de entorno en Render: para un deploy completo (migrate + app) necesita SECRET_KEY y
# DATABASE_URL en el panel. collectstatic del build puede ejecutarse sin SECRET_KEY (ver settings.py).
# =============================================================================
set -o errexit
set -o pipefail

cd "$(dirname "$0")"

echo "==> pip install (requirements.txt completo)"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

echo "==> collectstatic"
python manage.py collectstatic --no-input

echo "==> build.sh terminado OK"
