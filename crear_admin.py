"""
Crea usuarios iniciales (admin, etc.). Pensado para ejecutar manualmente tras el primer deploy,
no como parte obligatoria del build en Render.

Uso local o Shell de Render:  python crear_admin.py
"""
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "incasoft.settings")


def main() -> int:
    try:
        django.setup()
    except Exception as exc:
        print(f"No se pudo cargar Django: {exc}", file=sys.stderr)
        return 1

    from django.contrib.auth.models import Group, User
    from gestion.models import TipoIncapacidad

    def crear_tipos_incapacidad():
        tipos = [
            {"nombre": "Enfermedad General", "codigo": "EG", "entidad_responsable": "EPS", "dias_maximos": 180},
            {"nombre": "Enfermedad Profesional", "codigo": "EP", "entidad_responsable": "ARL", "dias_maximos": 180},
            {"nombre": "Accidente de Trabajo", "codigo": "AT", "entidad_responsable": "ARL", "dias_maximos": 180},
            {"nombre": "Licencia de Maternidad", "codigo": "LM", "entidad_responsable": "EPS", "dias_maximos": 126},
            {"nombre": "Licencia de Paternidad", "codigo": "LP", "entidad_responsable": "EPS", "dias_maximos": 14},
        ]
        for t in tipos:
            obj, created = TipoIncapacidad.objects.get_or_create(
                codigo=t["codigo"],
                defaults={
                    "nombre": t["nombre"],
                    "entidad_responsable": t["entidad_responsable"],
                    "dias_maximos": t["dias_maximos"]
                }
            )
            if created:
                print(f"✅ Tipo de Incapacidad creado: {t['nombre']} ({t['codigo']})")

    def crear_usuario(username, password, group_name=None, is_superuser=False):
        if User.objects.filter(username=username).exists():
            print(f"ℹ️ El usuario '{username}' ya existe.")
            return
        if is_superuser:
            user = User.objects.create_superuser(username, f"{username}@incasoft.com", password)
            print(f"✅ Superusuario '{username}' creado.")
        else:
            user = User.objects.create_user(username, f"{username}@incasoft.com", password)
            print(f"✅ Usuario '{username}' creado.")
        if group_name:
            grupo, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(grupo)
            print(f"   - Asignado al grupo: {group_name}")

    try:
        # Mismos nombres de grupo que seed_demo.py (sin tilde en "Gestion")
        crear_usuario("admin", "IncaSoft2026*", is_superuser=True)
        crear_usuario("gerente", "IncaSoft2026*", group_name="Gerente")
        crear_usuario("humana", "IncaSoft2026*", group_name="Gestion Humana")
        
        print("\nVerificando Tipos de Incapacidad requeridos...")
        crear_tipos_incapacidad()
    except Exception as exc:
        # No romper pipelines si alguien lo dejó en el build por error (BD, migraciones, etc.)
        print(f"⚠️ crear_admin.py no pudo completarse: {exc}", file=sys.stderr)
        print("   Ejecute de nuevo desde Render Shell cuando la app y la BD estén listas.", file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
