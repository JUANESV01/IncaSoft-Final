# INCASOFT — despliegue en Render.com

## Requisitos

- Cuenta en [Render](https://render.com)
- Una base **PostgreSQL** ya creada en Render (por ejemplo `incasoft-db`). **No hace falta crear otra:** en el **Web Service** use **Connect** → **Link database** y elija esa instancia; Render inyecta **`DATABASE_URL`** automáticamente (URL interna). Solo si enlaza a mano, pegue la **Internal Database URL** como variable `DATABASE_URL` (nunca suba esa URL a Git).
- Variables de entorno (ver abajo)

## Pasos rápidos

1. Conecte el repositorio Git a Render y cree un **Web Service** (runtime Python).
2. **Build command:** `chmod +x build.sh && ./build.sh`
3. **Start command:** `gunicorn incasoft.wsgi:application --bind 0.0.0.0:$PORT --timeout 120`  
   (Si usa el `Procfile` del repo, Render puede tomar el comando `web` automáticamente.)
4. En **Environment**, defina al menos:

| Variable | Descripción |
|----------|-------------|
| `DJANGO_SECRET_KEY` o `SECRET_KEY` | **Obligatorio** si `DJANGO_DEBUG=0` en Render: cadena aleatoria de **≥40 caracteres** (p. ej. `openssl rand -base64 48`). Sin esto el build falla al ejecutar `migrate`/`collectstatic`. |
| `DJANGO_DEBUG` | `0` en producción. |
| `DJANGO_ALLOWED_HOSTS` | Su dominio, p. ej. `incasoft.onrender.com` (sin `https://`). Render suele inyectar `RENDER_EXTERNAL_HOSTNAME`; el proyecto lo añade solo a `ALLOWED_HOSTS` si falta. |
| `DATABASE_URL` | La aporta Render al **vincular** su PostgreSQL existente al Web Service (recomendado). Si ya la tiene, no cambie nada salvo que el servicio web no esté enlazado a esa BD. |
| `GEMINI_API_KEY` | Opcional pero necesario para el botón de análisis IA en Reportes ([Google AI Studio](https://aistudio.google.com/apikey)). |
| `GEMINI_MODEL` | Opcional. Por defecto `gemini-2.0-flash`. Si falla, use `gemini-1.5-flash` o defina `GEMINI_MODEL_FALLBACKS`. |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Para recuperación de contraseña por correo (p. ej. SMTP Gmail con contraseña de aplicación). |
| `DJANGO_DEFAULT_FROM_EMAIL` | Remitente visible (a menudo igual que `EMAIL_HOST_USER`). |

5. **CSRF / HTTPS:** Si define `DJANGO_CSRF_TRUSTED_ORIGINS`, use la URL pública con esquema, p. ej. `https://incasoft.onrender.com`. Si no la define y existe `RENDER_EXTERNAL_HOSTNAME`, el proyecto configura `https://<host>` automáticamente.

6. Tras el primer despliegue, ejecute datos iniciales si lo necesita:  
   `python manage.py seed_demo` (solo en entornos controlados).

## Archivos de despliegue

- `Procfile`: `release` (migraciones) y `web` (Gunicorn en `0.0.0.0:$PORT`).
- `build.sh`: `pip install` + `collectstatic` (las migraciones van en `release`).
- `render.yaml`: blueprint de ejemplo (ajuste nombre de servicio y variables `sync: false`).

## Gemini (IA en reportes)

- Instalación: `google-generativeai` ya está en `requirements.txt`.
- Solo se envían **totales agregados** al modelo (sin nombres ni documentos).
- `GEMINI_MODEL_FALLBACKS` (coma separada): modelos alternativos si el principal no está disponible en su cuenta.
- `GEMINI_MAX_RETRIES`: reintentos ante fallos transitorios (por defecto 2).

## Archivos subidos (media)

En el plan estándar de Render el disco del contenedor es **efímero**: los PDF/imágenes pueden perderse al reiniciar. Para producción serio use un **Render Disk** montado en la ruta de `MEDIA_ROOT` o almacenamiento en la nube (S3, etc.).

## Comprobación local con variables similares a Render

```bash
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
export DATABASE_URL=postgresql://...
export RENDER=true
python manage.py check
```

Si falta PostgreSQL o la clave es insegura, `check` fallará con un mensaje explícito.
