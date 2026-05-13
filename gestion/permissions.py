"""Comprobaciones de roles reutilizables (vistas, decoradores, context processors)."""


def tiene_rol(user, *roles):
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def puede_gestionar_usuarios(user):
    return user.is_authenticated and tiene_rol(user, "Administrador")


def puede_editar_operacion(user):
    if not user.is_authenticated:
        return False
    return tiene_rol(user, "Administrador", "Gestion Humana", "Financiera", "Coordinacion")
