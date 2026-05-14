import os
import django

def reset():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "incasoft.settings")
    django.setup()

    from django.contrib.auth.models import User, Group
    from gestion.models import Incapacidad, Colaborador, TipoIncapacidad, HistorialEstado, Auditoria, Documento

    print("⚠️  INICIANDO LIMPIEZA TOTAL DE LA BASE DE DATOS...")
    
    # Borrar en orden para evitar errores de llave foránea
    print("- Borrando Documentos...")
    Documento.objects.all().delete()
    
    print("- Borrando Historial de estados...")
    HistorialEstado.objects.all().delete()
    
    print("- Borrando Incapacidades...")
    Incapacidad.objects.all().delete()
    
    print("- Borrando Colaboradores...")
    Colaborador.objects.all().delete()
    
    print("- Borrando Tipos de Incapacidad...")
    TipoIncapacidad.objects.all().delete()
    
    print("- Borrando Auditoría...")
    Auditoria.objects.all().delete()
    
    print("- Borrando Usuarios (excepto admin)...")
    User.objects.exclude(username='admin').delete()
    
    print("✅ LIMPIEZA COMPLETADA.")
    print("ℹ️  Los datos básicos se recrearán automáticamente al reiniciar la app vía crear_admin.py")

if __name__ == "__main__":
    reset()
