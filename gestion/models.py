import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone



class TipoIncapacidad(models.Model):
    ENTIDAD_CHOICES = [
        ("EPS", "EPS"),
        ("ARL", "ARL"),
        ("EMPRESA", "Empresa"),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    entidad_responsable = models.CharField(max_length=20, choices=ENTIDAD_CHOICES)
    dias_maximos = models.PositiveIntegerField(default=180)
    requiere_soporte = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "tipo de incapacidad"
        verbose_name_plural = "tipos de incapacidad"

    def __str__(self):
        return f"{self.nombre} ({self.entidad_responsable})"


class Colaborador(models.Model):
    DOCUMENTO_CHOICES = [
        ("CC", "Cedula de ciudadania"),
        ("CE", "Cedula de extranjeria"),
        ("TI", "Tarjeta de identidad"),
        ("PA", "Pasaporte"),
    ]

    tipo_documento = models.CharField(max_length=3, choices=DOCUMENTO_CHOICES, default="CC")
    numero_identificacion = models.CharField(max_length=30, unique=True)
    nombres = models.CharField(max_length=90)
    apellidos = models.CharField(max_length=90)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=25, blank=True)
    cargo = models.CharField(max_length=90)
    area = models.CharField(max_length=90)
    eps = models.CharField("EPS", max_length=120)
    arl = models.CharField("ARL", max_length=120, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.numero_identificacion}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    def get_absolute_url(self):
        return reverse("gestion:colaborador_detalle", args=[self.pk])


class Incapacidad(models.Model):
    ESTADO_RECIBIDA = "RECIBIDA"
    ESTADO_TRANSCRITA = "TRANSCRITA"
    ESTADO_COBRADA = "COBRADA"
    ESTADO_PAGADA = "PAGADA"
    ESTADO_RECHAZADA = "RECHAZADA"

    ESTADO_CHOICES = [
        (ESTADO_RECIBIDA, "Recibida"),
        (ESTADO_TRANSCRITA, "Transcrita"),
        (ESTADO_COBRADA, "Cobrada"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_RECHAZADA, "Rechazada"),
    ]

    TRANSICIONES_VALIDAS = {
        ESTADO_RECIBIDA: [ESTADO_TRANSCRITA, ESTADO_RECHAZADA],
        ESTADO_TRANSCRITA: [ESTADO_COBRADA, ESTADO_RECHAZADA],
        ESTADO_COBRADA: [ESTADO_PAGADA, ESTADO_RECHAZADA],
        ESTADO_PAGADA: [],
        ESTADO_RECHAZADA: [],
    }

    colaborador = models.ForeignKey(Colaborador, on_delete=models.PROTECT, related_name="incapacidades")
    tipo = models.ForeignKey(TipoIncapacidad, on_delete=models.PROTECT, related_name="incapacidades")
    entidad_responsable = models.CharField(max_length=120)
    numero_radicado = models.CharField(max_length=60, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveIntegerField(editable=False, default=1)
    dias_empresa = models.PositiveIntegerField(editable=False, default=0)
    dias_entidad = models.PositiveIntegerField(editable=False, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_RECIBIDA)
    soporte_medico = models.FileField(
        upload_to="soportes/%Y/%m/",
        validators=[
            FileExtensionValidator(
                ["pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx"]
            )
        ],
        blank=True,
    )
    observaciones = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incapacidades_creadas",
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incapacidades_actualizadas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_inicio", "fecha_fin"]),
        ]

    def __str__(self):
        return f"{self.colaborador.nombre_completo} - {self.get_estado_display()}"

    @property
    def esta_cerrada(self):
        return self.estado in {self.ESTADO_PAGADA, self.ESTADO_RECHAZADA}

    def get_absolute_url(self):
        return reverse("gestion:incapacidad_detalle", args=[self.pk])

    @property
    def soporte_extension(self):
        if not self.soporte_medico:
            return ""
        _, ext = os.path.splitext(self.soporte_medico.name)
        return ext.lstrip(".").lower()

    @property
    def soporte_nombre(self):
        if not self.soporte_medico:
            return ""
        return os.path.basename(self.soporte_medico.name)

    @property
    def soporte_es_imagen(self):
        return self.soporte_extension in {"png", "jpg", "jpeg"}

    @property
    def soporte_es_pdf(self):
        return self.soporte_extension == "pdf"

    @property
    def soporte_es_word(self):
        return self.soporte_extension in {"doc", "docx"}

    @property
    def soporte_es_excel(self):
        return self.soporte_extension in {"xls", "xlsx"}

    @property
    def soporte_size(self):
        try:
            return self.soporte_medico.size if self.soporte_medico else 0
        except Exception:
            return 0

    def clean(self):
        errors = {}
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            errors["fecha_fin"] = "La fecha final no puede ser anterior a la fecha inicial."

        if self.tipo and self.tipo.requiere_soporte and not self.soporte_medico:
            errors["soporte_medico"] = "Debe adjuntar el soporte medico en PDF o imagen."

        if self.colaborador_id and self.tipo_id and self.fecha_inicio and self.fecha_fin:
            duplicados = Incapacidad.objects.filter(
                colaborador=self.colaborador,
                tipo=self.tipo,
                fecha_inicio=self.fecha_inicio,
                fecha_fin=self.fecha_fin,
            )
            if self.pk:
                duplicados = duplicados.exclude(pk=self.pk)
            if duplicados.exists():
                errors["fecha_inicio"] = "Ya existe una incapacidad registrada para ese colaborador, tipo y rango."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.fecha_fin:
            self.dias = (self.fecha_fin - self.fecha_inicio).days + 1
        if self.tipo and not self.entidad_responsable:
            self.entidad_responsable = self.tipo.entidad_responsable
            
        # Cumplimiento de requerimientos (PDF):
        # EG: primeros 2 días los paga la empresa, el resto la EPS.
        # EP, AT, Maternidad, Paternidad: 100% desde el primer día la Entidad.
        if self.tipo:
            if self.tipo.codigo == "EG":
                self.dias_empresa = min(2, self.dias)
                self.dias_entidad = max(0, self.dias - 2)
            else:
                self.dias_empresa = 0
                self.dias_entidad = self.dias

        super().save(*args, **kwargs)

    def puede_transicionar_a(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES_VALIDAS.get(self.estado, [])

    def cambiar_estado(self, nuevo_estado, usuario=None, comentario=""):
        if not self.puede_transicionar_a(nuevo_estado):
            raise ValidationError(f"No se permite pasar de {self.get_estado_display()} a {nuevo_estado}.")
        anterior = self.estado
        self.estado = nuevo_estado
        self.actualizado_por = usuario
        self.save(update_fields=["estado", "actualizado_por", "fecha_actualizacion"])
        HistorialEstado.objects.create(
            incapacidad=self,
            estado_anterior=anterior,
            estado_nuevo=nuevo_estado,
            comentario=comentario,
            usuario=usuario,
        )


class HistorialEstado(models.Model):
    incapacidad = models.ForeignKey(Incapacidad, on_delete=models.CASCADE, related_name="historial")
    estado_anterior = models.CharField(max_length=20, choices=Incapacidad.ESTADO_CHOICES)
    estado_nuevo = models.CharField(max_length=20, choices=Incapacidad.ESTADO_CHOICES)
    comentario = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.incapacidad_id}: {self.estado_anterior} -> {self.estado_nuevo}"


class Documento(models.Model):
    """Archivo adjunto (PDF, Word, imagen) vinculado a una incapacidad."""

    TIPO_CHOICES = [
        ("SOPORTE", "Soporte médico"),
        ("EPICRISIS", "Epicrisis"),
        ("FURIPS", "FURIPS (Accidente Tránsito)"),
        ("FORMULA", "Fórmula médica"),
        ("CARTA", "Carta / Comunicación"),
        ("LIQUIDACION", "Liquidación"),
        ("OTRO", "Otro"),
    ]

    incapacidad = models.ForeignKey(
        Incapacidad, on_delete=models.CASCADE, related_name="documentos"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="SOPORTE")
    nombre = models.CharField(max_length=200, blank=True, help_text="Descripción opcional del documento")
    archivo = models.FileField(
        upload_to="documentos/%Y/%m/",
        validators=[
            FileExtensionValidator(
                ["pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx"]
            )
        ],
    )
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_subidos",
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_subida"]
        verbose_name = "documento"
        verbose_name_plural = "documentos"

    def __str__(self):
        return self.nombre or self.archivo.name

    @property
    def extension(self):
        """Devuelve la extensión en minúsculas, sin el punto."""
        _, ext = os.path.splitext(self.archivo.name)
        return ext.lstrip(".").lower()

    @property
    def es_imagen(self):
        return self.extension in {"png", "jpg", "jpeg"}

    @property
    def es_pdf(self):
        return self.extension == "pdf"

    @property
    def es_word(self):
        return self.extension in {"doc", "docx"}

    @property
    def es_excel(self):
        return self.extension in {"xls", "xlsx"}

    @property
    def archivo_size(self):
        try:
            return self.archivo.size if self.archivo else 0
        except Exception:
            return 0


class Auditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=160)
    detalle = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "auditoria"
        verbose_name_plural = "auditorias"

    def __str__(self):
        return self.accion
