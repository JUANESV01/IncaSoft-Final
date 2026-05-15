#!/usr/bin/env bash
# =============================================================================
# Build para Render.com - Versión Blindada
# =============================================================================
set -o errexit

echo "==> Instalando dependencias..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "==> Preparando archivos estáticos..."
python manage.py collectstatic --no-input

# echo "==> RESET TOTAL DE BASE DE DATOS (Limpieza de fábrica)..."
# python reset_db.py

echo "==> Aplicando migraciones finales..."
python manage.py migrate --no-input

echo "==> Build finalizado con éxito."
