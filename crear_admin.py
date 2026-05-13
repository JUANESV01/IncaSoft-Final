import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incasoft.settings')
django.setup()

from django.contrib.auth.models import User, Group

def crear_usuario(username, password, group_name=None, is_superuser=False):
    if not User.objects.filter(username=username).exists():
        if is_superuser:
            user = User.objects.create_superuser(username, f'{username}@incasoft.com', password)
            print(f"✅ Superusuario '{username}' creado.")
        else:
            user = User.objects.create_user(username, f'{username}@incasoft.com', password)
            print(f"✅ Usuario '{username}' creado.")
        
        if group_name:
            grupo, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(grupo)
            print(f"   - Asignado al grupo: {group_name}")
    else:
        print(f"ℹ️ El usuario '{username}' ya existe.")

# Crear usuarios por defecto
crear_usuario('admin', 'IncaSoft2026*', is_superuser=True)
crear_usuario('gerente', 'IncaSoft2026*', group_name='Gerencia')
crear_usuario('humana', 'IncaSoft2026*', group_name='Gestión Humana')
