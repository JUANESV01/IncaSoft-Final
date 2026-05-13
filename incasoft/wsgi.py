"""
WSGI config for incasoft project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incasoft.settings')

application = get_wsgi_application()

# Forzar migraciones automáticamente al arrancar Gunicorn
# Esto asegura que las tablas existan incluso si Render ignora los comandos de release.
try:
    from django.core.management import call_command
    print("Ejecutando migraciones automáticamente desde wsgi.py...", file=sys.stderr)
    call_command('migrate', interactive=False)
    
    # Auto-crear usuarios si no existen
    try:
        import crear_admin
        print("Verificando usuarios predeterminados...", file=sys.stderr)
        crear_admin.main()
    except Exception as e2:
        print(f"Error al crear usuarios predeterminados: {e2}", file=sys.stderr)

except Exception as e:
    print(f"Error al ejecutar migraciones: {e}", file=sys.stderr)

