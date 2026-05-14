import os
import django

def reset():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "incasoft.settings")
    django.setup()

    from django.contrib.auth.models import User, Group
    from gestion.models import Incapacidad, Colaborador, TipoIncapacidad, HistorialEstado, Auditoria, Documento
    from crear_admin import main as recrear_todo

    print("⚠️  INICIANDO RESET TOTAL DE FÁBRICA...")
    
    # Borrado masivo
    Documento.objects.all().delete()
    HistorialEstado.objects.all().delete()
    Incapacidad.objects.all().delete()
    Colaborador.objects.all().delete()
    TipoIncapacidad.objects.all().delete()
    Auditoria.objects.all().delete()
    User.objects.all().delete() # Borramos TODO para evitar conflictos
    Group.objects.all().delete()
    
    print("✅ BASE DE DATOS LIMPIA.")
    print("🔄 RECREANDO DATOS INICIALES...")
    recrear_todo()
    print("✨ SISTEMA RESTAURADO Y LISTO.")

if __name__ == "__main__":
    reset()
