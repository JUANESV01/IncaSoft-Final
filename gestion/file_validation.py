"""
Validación centralizada de archivos subidos (extensión, tamaño, firma binaria básica).
Evita depender solo de la extensión o del Content-Type enviado por el cliente.
"""

import os
import zipfile
from typing import BinaryIO

from django.core.exceptions import ValidationError

# ── Configuración centralizada ───────────────────────────────────────────────

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

# Extensiones permitidas (minúsculas, sin punto)
ALLOWED_EXTENSIONS = frozenset(
    {"pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx"}
)

# Firmas mágicas mínimas (primeros bytes del archivo)
_MAGIC_CHECKS = {
    "pdf": (b"%PDF",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    # DOCX / XLSX: ZIP “PK”
    "docx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    "xlsx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    # OLE2 (DOC / XLS antiguos)
    "doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    "xls": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
}


def _extensiones_peligrosas(nombre: str) -> bool:
    """Detecta doble extensión u otras extensiones de riesgo en el nombre."""
    base = os.path.basename(nombre or "").lower()
    partes = base.split(".")
    if len(partes) < 2:
        return False
    # Todas las extensiones del nombre deben estar en la lista blanca
    exts = [p for p in partes[1:] if p]
    if not exts:
        return False
    for e in exts:
        if e not in ALLOWED_EXTENSIONS:
            return True
    return False


def _leer_cabecera(f: BinaryIO, n: int = 16) -> bytes:
    pos = f.tell()
    try:
        chunk = f.read(n)
        return chunk
    finally:
        f.seek(pos)


def validar_archivo_subido(
    archivo,
    *,
    permitir_vacio: bool = False,
) -> None:
    """
    Valida un UploadedFile o FileField file:
    - nombre y extensión
    - tamaño
    - firma binaria vs extensión declarada
    """
    if archivo is None or (hasattr(archivo, "name") and not archivo.name):
        if permitir_vacio:
            return
        raise ValidationError(["Debe seleccionar un archivo."])

    nombre = getattr(archivo, "name", "") or ""
    if _extensiones_peligrosas(nombre):
        raise ValidationError(
            [
                "El nombre del archivo no es válido o contiene extensiones no permitidas."
            ]
        )

    ext = os.path.splitext(nombre)[1].lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            [
                "Tipo de archivo no permitido. Use PDF, Word, Excel o imagen "
                "(PNG, JPG, JPEG) según corresponda."
            ]
        )

    size = getattr(archivo, "size", None)
    if size is not None and size > MAX_UPLOAD_BYTES:
        mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        raise ValidationError(
            [f"El archivo supera el tamaño máximo permitido ({mb} MB)."]
        )

    magic_ok = _MAGIC_CHECKS.get(ext)
    if magic_ok:
        head = _leer_cabecera(archivo, n=32)
        if not any(head.startswith(sig) for sig in magic_ok):
            raise ValidationError(
                [
                    "El contenido del archivo no coincide con el tipo declarado. "
                    "Compruebe que el archivo no esté dañado o renombrado."
                ]
            )

    # Office Open XML: comprobar estructura interna (evita ZIP arbitrario con extensión .docx/.xlsx)
    if ext == "docx":
        try:
            archivo.seek(0)
            with zipfile.ZipFile(archivo) as zf:
                if "word/document.xml" not in zf.namelist():
                    raise ValidationError(
                        ["El archivo no es un documento Word válido (.docx)."]
                    )
        except zipfile.BadZipFile as exc:
            raise ValidationError(
                ["El archivo DOCX está corrupto o no es un paquete Office válido."]
            ) from exc
        finally:
            archivo.seek(0)
    elif ext == "xlsx":
        try:
            archivo.seek(0)
            with zipfile.ZipFile(archivo) as zf:
                if "xl/workbook.xml" not in zf.namelist():
                    raise ValidationError(
                        ["El archivo no es una hoja de cálculo Excel válida (.xlsx)."]
                    )
        except zipfile.BadZipFile as exc:
            raise ValidationError(
                ["El archivo XLSX está corrupto o no es un paquete Office válido."]
            ) from exc
        finally:
            archivo.seek(0)
