#!/usr/bin/env bash
# =============================================================================
# Build para Render.com (o CI)
# =============================================================================
# Este script:
#   1) Instala TODO lo declarado en requirements.txt (Django, psycopg, Gemini, etc.)
#   2) Ejecuta collectstatic para servir CSS/JS/logo con WhiteNoise
#   3) Opcional: django check (falla rápido si falta SECRET_KEY u otra config grave)
#
# NO hace:
#   - No borra ni recrea la base de datos; los datos existentes en PostgreSQL se conservan.
#   - No ejecuta migraciones aquí (las hace Render con el comando "release" del Procfile).
#   - No crea usuarios (eso es: Render Shell → python crear_admin.py o seed_demo).
#
# Variables de entorno en Render deben estar listas antes del build (SECRET_KEY, DATABASE_URL, …).
# =============================================================================
set -o errexit
set -o pipefail

cd "$(dirname "$0")"

echo "==> pip install (requirements.txt completo)"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

echo "==> django check (configuración básica)"
python manage.py check

echo "==> collectstatic"
python manage.py collectstatic --no-input

echo "==> build.sh terminado OK"
