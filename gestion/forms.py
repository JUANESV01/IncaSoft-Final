from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from .file_validation import MAX_UPLOAD_BYTES, validar_archivo_subido
from .models import Colaborador, Documento, Incapacidad, TipoIncapacidad


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
        self.fields["soporte_medico"].help_text = (
            f"PDF, Word, Excel o imagen. Tamaño máximo {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
        )

    def clean_soporte_medico(self):
        archivo = self.cleaned_data.get("soporte_medico")
        if not archivo:
            return archivo
        validar_archivo_subido(archivo, permitir_vacio=False)
        return archivo

    def clean(self):
        cleaned = super().clean()
        # El radicado se genera automáticamente en el save() del modelo
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
    group = forms.ModelChoiceField(
        label="Rol",
        queryset=Group.objects.order_by("name"),
        required=True,
        empty_label=None,
        help_text="Cada usuario debe tener exactamente un rol de aplicación.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email") or ""
        user.first_name = self.cleaned_data.get("first_name") or ""
        user.last_name = self.cleaned_data.get("last_name") or ""
        grupo = self.cleaned_data.get("group")
        if commit:
            user.save()
            if grupo:
                user.groups.set([grupo])
        return user


class UsuarioActualizarForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        label="Rol",
        queryset=Group.objects.order_by("name"),
        required=True,
        help_text="Un solo rol por usuario.",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].empty_label = None
        if self.instance.pk:
            actual = self.instance.groups.first()
            if actual:
                self.fields["group"].initial = actual.pk
            else:
                self.fields["group"].empty_label = "Seleccione un rol"

    def save(self, commit=True):
        user = super().save(commit=commit)
        grupo = self.cleaned_data.get("group")
        if commit and grupo:
            user.groups.set([grupo])
        return user


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ["tipo", "nombre", "archivo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Descripción opcional del archivo"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].help_text = (
            f"PDF, Word, Excel o imagen. Tamaño máximo {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
        )

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")
        if archivo:
            validar_archivo_subido(archivo, permitir_vacio=False)
        return archivo
