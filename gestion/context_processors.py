from .permissions import puede_gestionar_usuarios


def permisos_ui(request):
    return {
        "puede_gestionar_usuarios": puede_gestionar_usuarios(request.user)
        if request.user.is_authenticated
        else False,
    }
