from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from .models import Colaborador, Documento, Incapacidad, TipoIncapacidad

# Máximo 10 MB por archivo
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
EXTENSIONES_PERMITIDAS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}


class DateInput(forms.DateInput):
    input_type = "date"


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = [
            "tipo_documento",
            "numero_identificacion",
            "nombres",
            "apellidos",
            "correo",
            "telefono",
            "cargo",
            "area",
            "eps",
            "arl",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["numero_identificacion"].disabled = True


class IncapacidadForm(forms.ModelForm):
    class Meta:
        model = Incapacidad
        fields = [
            "colaborador",
            "tipo",
            "entidad_responsable",
            "numero_radicado",
            "fecha_inicio",
            "fecha_fin",
            "soporte_medico",
            "observaciones",
        ]
        widgets = {
            "fecha_inicio": DateInput(),
            "fecha_fin": DateInput(),
            "observaciones": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["colaborador"].queryset = Colaborador.objects.filter(activo=True)
        self.fields["tipo"].queryset = TipoIncapacidad.objects.filter(activo=True)
        self.fields["colaborador"].empty_label = "Seleccione un colaborador"
        self.fields["tipo"].empty_label = "Seleccione el tipo"
        self.fields["entidad_responsable"].help_text = "EPS, ARL o entidad responsable del cobro."

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get("tipo")
        entidad = cleaned.get("entidad_responsable")
        if tipo and not entidad:
            cleaned["entidad_responsable"] = tipo.entidad_responsable
        return cleaned


class EstadoIncapacidadForm(forms.Form):
    estado = forms.ChoiceField(label="Nuevo estado")
    comentario = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, incapacidad, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.incapacidad = incapacidad
        opciones = [
            choice
            for choice in Incapacidad.ESTADO_CHOICES
            if choice[0] in Incapacidad.TRANSICIONES_VALIDAS.get(incapacidad.estado, [])
        ]
        self.fields["estado"].choices = opciones
        if not opciones:
            self.fields["estado"].disabled = True
            self.fields["estado"].help_text = "La incapacidad ya esta en un estado final."

    def clean_estado(self):
        estado = self.cleaned_data["estado"]
        if not self.incapacidad.puede_transicionar_a(estado):
            raise ValidationError("La transicion seleccionada no esta permitida.")
        return estado


class IncapacidadFiltroForm(forms.Form):
    q = forms.CharField(label="Busqueda", required=False)
    estado = forms.ChoiceField(label="Estado", required=False)
    tipo = forms.ModelChoiceField(label="Tipo", queryset=TipoIncapacidad.objects.none(), required=False)
    fecha_inicio = forms.DateField(label="Desde", required=False, widget=DateInput())
    fecha_fin = forms.DateField(label="Hasta", required=False, widget=DateInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estado"].choices = [("", "Todos los estados")] + Incapacidad.ESTADO_CHOICES
        self.fields["tipo"].queryset = TipoIncapacidad.objects.filter(activo=True)
        self.fields["tipo"].empty_label = "Todos los tipos"


class UsuarioCrearForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(label="Nombres", required=False)
    last_name = forms.CharField(label="Apellidos", required=False)
    groups = forms.ModelMultipleChoiceField(
        label="Roles",
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "groups")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            self.save_m2m()
        return user


class UsuarioActualizarForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        label="Roles",
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "groups")


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ["tipo", "nombre", "archivo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Descripción opcional del archivo"}),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")
        if archivo:
            import os
            ext = os.path.splitext(archivo.name)[1].lstrip(".").lower()
            if ext not in EXTENSIONES_PERMITIDAS:
                raise ValidationError(
                    f"Formato no permitido (.{ext}). Use: PDF, Word (.doc/.docx) o imagen (PNG/JPG)."
                )
            if archivo.size > MAX_UPLOAD_SIZE:
                raise ValidationError(
                    f"El archivo supera el límite de 10 MB ({archivo.size // (1024*1024)} MB)."
                )
        return archivo
