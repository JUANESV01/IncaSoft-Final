#!/usr/bin/env bash
# Construcción para Render (o CI). Las migraciones las ejecuta el comando "release" del Procfile.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
