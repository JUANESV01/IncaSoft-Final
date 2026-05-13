"""Vistas de autenticación con contexto adicional para plantillas."""

from django.conf import settings
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView


class PasswordResetView(DjangoPasswordResetView):
    """Añade banderas para mostrar ayuda sobre envío de correo (SMTP)."""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        host = getattr(settings, "EMAIL_HOST", "") or ""
        ctx["email_smtp_activo"] = bool(host.strip())
        ctx["email_from_display"] = getattr(settings, "DEFAULT_FROM_EMAIL", "")
        return ctx
