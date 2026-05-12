#!/bin/bash
# Lanzador automático para INCASOFT Solutions

# Obtener la ruta donde está el archivo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================"
echo "   INICIANDO INCASOFT SOLUTIONS"
echo "========================================"

# 1. Intentar iniciar Postgres si no está corriendo (asumiendo instalación estándar)
if ! pg_isready -q; then
    echo "Starting PostgreSQL..."
    export PATH="/Library/PostgreSQL/18/bin:$PATH"
    # Nota: Esto asume que Postgres se inicia con el sistema o requiere permisos
fi

# 2. Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: No se encontró la carpeta venv. Ejecuta la instalación primero."
    exit 1
fi

# 3. Abrir el navegador automáticamente
sleep 2
open "http://127.0.0.1:8000"

# 4. Iniciar el servidor
echo "Servidor activo en http://127.0.0.1:8000"
echo "Para cerrar: Presiona CTRL+C"
python manage.py runserver
