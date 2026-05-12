#!/usr/bin/env bash
# Script de construcción para Render
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos (CSS, JS, Imágenes)
python manage.py collectstatic --no-input

# Aplicar migraciones de base de datos
python manage.py migrate
