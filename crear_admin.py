import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incasoft.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@example.com'
password = 'IncaSoft2026*'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superusuario '{username}' creado exitosamente.")
else:
    print(f"ℹ️ El usuario '{username}' ya existe.")
