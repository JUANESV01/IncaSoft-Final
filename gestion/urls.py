from django.urls import path

from . import views

app_name = "gestion"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("incapacidades/", views.incapacidad_lista, name="incapacidad_lista"),
    path("incapacidades/nueva/", views.incapacidad_crear, name="incapacidad_crear"),
    path("incapacidades/<int:pk>/", views.incapacidad_detalle, name="incapacidad_detalle"),
    path("incapacidades/<int:pk>/estado/", views.incapacidad_estado, name="incapacidad_estado"),
    path("colaboradores/", views.colaborador_lista, name="colaborador_lista"),
    path("colaboradores/nuevo/", views.colaborador_crear, name="colaborador_crear"),
    path("colaboradores/<int:pk>/", views.colaborador_detalle, name="colaborador_detalle"),
    path("colaboradores/<int:pk>/editar/", views.colaborador_editar, name="colaborador_editar"),
    path("reportes/", views.reportes, name="reportes"),
    path("reportes/pdf/", views.reportes_pdf, name="reportes_pdf"),
    path("usuarios/", views.usuario_lista, name="usuario_lista"),
    path("usuarios/nuevo/", views.usuario_crear, name="usuario_crear"),
    path("usuarios/<int:pk>/editar/", views.usuario_editar, name="usuario_editar"),
    # Documentos adjuntos
    path("incapacidades/<int:incapacidad_pk>/documentos/subir/", views.documento_subir, name="documento_subir"),
    path("documentos/<int:pk>/eliminar/", views.documento_eliminar, name="documento_eliminar"),
]
