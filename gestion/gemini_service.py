"""
Análisis de reportes con Google Gemini (API según cuota de Google AI Studio).
Solo se envían agregados estadísticos, sin datos personales identificables.
"""

from __future__ import annotations

import time
from typing import Any, Sequence

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _mapear_estados(por_estado: list[dict[str, Any]], labels: dict[str, str]) -> str:
    lineas = []
    for item in por_estado:
        codigo = item.get("estado", "")
        total = item.get("total", 0)
        nombre = labels.get(codigo, codigo)
        lineas.append(f"  - {nombre} ({codigo}): {total} casos")
    return "\n".join(lineas) if lineas else "  (sin desglose)"


def construir_resumen_agregado(
    *,
    total: int,
    dias: int,
    por_estado: list[dict[str, Any]],
    por_tipo: list[dict[str, Any]],
    por_mes: list[dict[str, Any]],
    estado_labels: dict[str, str],
) -> str:
    bloques = [
        f"Total de incapacidades en el filtro: {total}",
        f"Suma de días de incapacidad: {dias}",
        "Distribución por estado:",
        _mapear_estados(por_estado, estado_labels),
        "Distribución por tipo de incapacidad:",
    ]
    for item in por_tipo:
        nombre = item.get("tipo__nombre", "Sin nombre")
        bloques.append(f"  - {nombre}: {item.get('total', 0)} casos")
    if not por_tipo:
        bloques.append("  (sin datos)")
    bloques.append("Evolución mensual (por fecha de inicio):")
    for item in por_mes:
        bloques.append(f"  - {item.get('mes', '?')}: {item.get('total', 0)} casos")
    if not por_mes:
        bloques.append("  (sin datos)")
    return "\n".join(bloques)


def _modelos_a_probar(modelo_principal: str, fallbacks: Sequence[str]) -> list[str]:
    vistos: set[str] = set()
    orden: list[str] = []
    for m in (modelo_principal, *fallbacks):
        m = (m or "").strip()
        if not m or m in vistos:
            continue
        vistos.add(m)
        orden.append(m)
    return orden


def _es_error_modelo_no_disponible(exc: BaseException, google_api_exceptions) -> bool:
    msg = str(exc).lower()
    if any(x in msg for x in ("not found", "404", "invalid model", "unsupported", "does not exist")):
        return True
    if google_api_exceptions and isinstance(exc, google_api_exceptions.InvalidArgument):
        return True
    if google_api_exceptions:
        nf = getattr(google_api_exceptions, "NotFound", None)
        if nf is not None and isinstance(exc, nf):
            return True
    return False


def _es_error_transitorio(exc: BaseException, google_api_exceptions) -> bool:
    if google_api_exceptions and isinstance(
        exc,
        (
            google_api_exceptions.ResourceExhausted,
            google_api_exceptions.ServiceUnavailable,
            google_api_exceptions.DeadlineExceeded,
            google_api_exceptions.InternalServerError,
        ),
    ):
        return True
    msg = str(exc).lower()
    return "timeout" in msg or "temporar" in msg or "503" in msg or "429" in msg or "cuota" in msg


def _llamar_gemini_una_vez(
    prompt: str,
    *,
    api_key: str,
    model_name: str,
) -> str:
    import google.generativeai as genai

    try:
        from google.api_core import exceptions as google_api_exceptions
    except ImportError:
        google_api_exceptions = None  # type: ignore[assignment]

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.35, "max_output_tokens": 2048},
        )
    except Exception as exc:
        if google_api_exceptions and isinstance(exc, google_api_exceptions.PermissionDenied):
            raise ValueError(
                "La API de Gemini rechazó la clave. Revise GEMINI_API_KEY en el panel de Google AI Studio."
            ) from exc
        raise

    try:
        texto = (response.text or "").strip()
    except (ValueError, AttributeError) as exc:
        raise ValueError(
            "No se pudo leer la respuesta del modelo (posible bloqueo de seguridad). "
            "Intente de nuevo con otros filtros."
        ) from exc

    if not texto:
        raise ValueError("El modelo no devolvió texto. Intente de nuevo.")

    return texto


def generar_analisis_gemini(
    resumen_texto: str,
    *,
    api_key: str,
    model_name: str | None = None,
) -> str:
    """
    Genera el análisis. Prueba modelos alternativos (GEMINI_MODEL_FALLBACKS) si el principal
    no está disponible, y reintenta en fallos transitorios de red o cuota momentánea.
    """
    if not api_key:
        raise ImproperlyConfigured("GEMINI_API_KEY no está configurada.")

    try:
        import google.generativeai as genai  # noqa: F401
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Instale la dependencia: pip install google-generativeai"
        ) from exc

    try:
        from google.api_core import exceptions as google_api_exceptions
    except ImportError:
        google_api_exceptions = None  # type: ignore[assignment]

    principal = (model_name or getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")).strip()
    fallbacks = getattr(settings, "GEMINI_MODEL_FALLBACKS", ())
    max_retries = max(0, int(getattr(settings, "GEMINI_MAX_RETRIES", 2)))

    prompt = f"""Eres un analista de gestión humana y salud ocupacional en Colombia (empresa, incapacidades EPS/ARL).

A continuación tienes ÚNICAMENTE datos agregados de un reporte interno de incapacidades. No hay nombres de personas ni números de documento.

Tarea: redacta un análisis breve y profesional en español (entre 4 y 8 párrafos cortos) que cubra:
1) Lectura del flujo por estados (Recibida → Transcrita → Cobrada → Pagada, y Rechazada si aplica).
2) Tipos de incapacidad más frecuentes y posible foco operativo (sin diagnosticar individuos).
3) Patrón temporal por meses y picos o vacíos.
4) Tres a cinco recomendaciones de seguimiento genéricas (priorización, comunicación con EPS/ARL, revisión de cuellos de botella), sin afirmaciones médicas ni legales definitivas.

Si total de casos es 0, indica que no hay datos y sugiere ajustar filtros.

Datos agregados:
{resumen_texto}
"""

    modelos = _modelos_a_probar(principal, fallbacks)
    ultimo_error: BaseException | None = None

    for modelo in modelos:
        for intento in range(max_retries + 1):
            try:
                return _llamar_gemini_una_vez(
                    prompt,
                    api_key=api_key,
                    model_name=modelo,
                )
            except ValueError as exc:
                ultimo_error = exc
                if _es_error_transitorio(exc, google_api_exceptions) and intento < max_retries:
                    time.sleep(1.0 + intento * 0.5)
                    continue
                raise
            except Exception as exc:
                ultimo_error = exc
                if google_api_exceptions and isinstance(
                    exc, google_api_exceptions.ResourceExhausted
                ):
                    if intento < max_retries:
                        time.sleep(1.5 + intento * 0.5)
                        continue
                    raise ValueError(
                        "Cuota o límite de solicitudes de Gemini alcanzado. Intente más tarde."
                    ) from exc
                if _es_error_modelo_no_disponible(exc, google_api_exceptions):
                    break
                if _es_error_transitorio(exc, google_api_exceptions) and intento < max_retries:
                    time.sleep(1.0 + intento * 0.5)
                    continue
                if google_api_exceptions and isinstance(exc, google_api_exceptions.PermissionDenied):
                    raise ValueError(
                        "La API de Gemini rechazó la clave. Revise GEMINI_API_KEY."
                    ) from exc
                raise ValueError(f"No se pudo contactar a Gemini: {exc}") from exc

    raise ValueError(
        "Ningún modelo de Gemini configurado respondió. "
        "Ajuste GEMINI_MODEL o GEMINI_MODEL_FALLBACKS según los modelos disponibles en Google AI Studio."
    ) from ultimo_error


def analizar_documento_incapacidad(
    file_content: bytes,
    file_mime: str,
    *,
    api_key: str,
    model_name: str | None = None,
) -> dict[str, Any]:
    """
    Envía un archivo (imagen o PDF) a Gemini para extraer datos de la incapacidad.
    Retorna un diccionario con: fecha_inicio, fecha_fin, tipo_sugerido, confianza.
    """
    import json as py_json
    import google.generativeai as genai

    if not api_key:
        return {"error": "API Key no configurada"}

    genai.configure(api_key=api_key)
    model_name = (model_name or getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")).strip()
    model = genai.GenerativeModel(model_name)

    prompt = """Analiza este documento médico de incapacidad en Colombia y extrae la siguiente información en formato JSON puro (sin bloques de código markdown):
    {
      "fecha_inicio": "YYYY-MM-DD",
      "fecha_fin": "YYYY-MM-DD",
      "tipo_sugerido": "EG|EP|AT|LM|LP",
      "resumen": "breve resumen del diagnostico o motivo",
      "confianza": 0.0 a 1.0
    }
    Tipos: EG (Enfermedad General), EP (Enfermedad Profesional), AT (Accidente Trabajo), LM (Maternidad), LP (Paternidad).
    Si no puedes determinar algo, deja el valor como null. No inventes datos.
    Responde ÚNICAMENTE el JSON.
    """

    try:
        # Preparar el archivo para Gemini
        content = [
            {"mime_type": file_mime, "data": file_content},
            prompt
        ]
        response = model.generate_content(content)
        texto = response.text.strip()
        # Limpiar posibles bloques de código markdown
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:].strip()
            texto = texto.strip()
        
        return py_json.loads(texto)
    except Exception as e:
        return {"error": str(e)}
