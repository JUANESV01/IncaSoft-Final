#!/usr/bin/env bash
# =============================================================================
# Build para Render.com (o CI)
# =============================================================================
# Este script:
#   1) Instala TODO lo declarado en requirements.txt
#   2) Ejecuta collectstatic para servir los archivos CSS/JS con WhiteNoise
#
# Las migraciones a la base de datos se ejecutan automáticamente al arrancar Gunicorn
# gracias a la lógica que incluimos en incasoft/wsgi.py.
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
