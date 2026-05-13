# INCASOFT Solutions — Gestión de incapacidades

Plataforma web empresarial para el **registro, seguimiento y reporte** de incapacidades laborales y licencias (EPS, ARL, empresa), con **control por roles**, **adjuntos de documentos**, **reportes** (incluido exportación a vista PDF) y **análisis asistido por IA** (Google Gemini) sobre datos agregados.

---

## Descripción del proyecto

INCASOFT permite a las áreas de talento humano, coordinación y finanzas:

- Gestionar **colaboradores** y sus datos de contacto, EPS/ARL y área.
- Registrar **incapacidades** con tipo, fechas, radicado, observaciones y **soporte médico** (PDF, imágenes, Office según configuración).
- Seguir el **ciclo de estados**: Recibida → Transcrita → Cobrada → Pagada (y Rechazada cuando aplica), con **historial** y trazabilidad.
- **Adjuntar documentos** adicionales por caso, con descarga/visualización autenticada.
- Consultar **reportes** con filtros, gráficos en el navegador y **exportación PDF**; opcionalmente generar un **texto de análisis** con Gemini a partir de totales (sin enviar datos personales a la IA).
- Administrar **usuarios y un rol por usuario** (grupos de Django); solo el perfil **Administrador** crea usuarios.
- **Recuperación de contraseña** por correo (SMTP configurable).
- **Auditoría** de acciones relevantes en el sistema.

El interfaz está en **español (Colombia)**, con diseño responsive, modo visual claro/oscuro según estilos del proyecto y formularios accesibles básicos.

---

## Stack tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Lenguaje** | Python 3 |
| **Framework web** | [Django](https://www.djangoproject.com/) 6.x |
| **Servidor de aplicación** | [Gunicorn](https://gunicorn.org/) |
| **ASGI/WSGI** | `incasoft.wsgi` / `incasoft.asgi` (Django estándar) |
| **Base de datos** | [PostgreSQL](https://www.postgresql.org/) en producción (p. ej. Render); [SQLite](https://www.sqlite.org/) opcional en desarrollo |
| **Adaptador PostgreSQL** | [psycopg](https://www.psycopg.org/) 3 (binario incluido en `requirements.txt`) |
| **URL de base de datos** | [dj-database-url](https://github.com/jazzband/dj-database-url) (`DATABASE_URL` en Render, Heroku, etc.) |
| **Archivos estáticos** | [WhiteNoise](http://whitenoise.evans.io/) (compresión y caché en producción) |
| **Plantillas** | Django Templates (HTML) |
| **Estilos** | CSS propio (`gestion/static/gestion/css/styles.css`) |
| **Gráficos en reportes** | JavaScript en canvas (sin librería de gráficos externa; `gestion/static/gestion/js/charts.js`) |
| **Autenticación** | `django.contrib.auth` (sesiones, login, logout, recuperación de contraseña) |
| **Roles** | `django.contrib.auth.models.Group` |
| **Internacionalización** | `LANGUAGE_CODE=es-co`, `TIME_ZONE=America/Bogota` |
| **Humanización** | `django.contrib.humanize` (tamaños de archivo, etc.) |
| **IA (reportes)** | [Google Generative AI SDK](https://ai.google.dev/) (`google-generativeai`) — modelo configurable (p. ej. Gemini Flash) |
| **Validación de archivos** | Validadores Django + lógica propia (`gestion/file_validation.py`: extensiones, tamaño, firmas mágicas, Office Open XML) |
| **Despliegue** | [Render.com](https://render.com) (documentado en este README; `Procfile`, `build.sh`, `render.yaml` de ejemplo) |
| **Otros** | `sqlparse`, `tzdata`; variables por archivo `.env` (carga en `incasoft/settings.py`) |

---

## Requisitos previos

- Python 3.12+ recomendado (compatible con 3.14 según entorno).
- Para producción: PostgreSQL y variables de entorno configuradas.

---

## Instalación local rápida

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Opcional: datos de demostración y roles — `python manage.py seed_demo`  
Opcional: usuario admin — `python crear_admin.py`

---

## Render.com — Web Service

### Build Command (copiar y pegar exactamente)

```text
chmod +x build.sh && ./build.sh
```

Ese comando:

1. Instala **todas** las dependencias de `requirements.txt`.
2. Ejecuta **`collectstatic`** para WhiteNoise.

El paso **Release** del `Procfile` (`migrate`) y el arranque con **Gunicorn** siguen exigiendo **`DJANGO_SECRET_KEY` o `SECRET_KEY`** (≥40 caracteres) y **`DATABASE_URL`** definidos en el panel de Render — añádalos **antes** del deploy o el release/web fallará con un mensaje claro.

**No** incluya aquí `migrate` ni `crear_admin.py` (evita fallos y duplicados; las migraciones van en el **Release** del `Procfile`).

### Start Command

Deje vacío si Render detecta el **`Procfile`** del repositorio. Si debe escribirlo a mano:

```text
gunicorn incasoft.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
```

El `Procfile` define además:

- `release: python manage.py migrate --noinput` — aplica migraciones **sin borrar** datos existentes.
- `web: gunicorn ...` — arranque del servicio.

### Base de datos

Si ya tiene una instancia PostgreSQL en Render (p. ej. `incasoft-db`): en el Web Service → **Connect** → **Link database**. Render inyecta **`DATABASE_URL`**. No suba credenciales al repositorio Git.

### Variables de entorno recomendadas

| Variable | Descripción |
|----------|-------------|
| `DJANGO_SECRET_KEY` o `SECRET_KEY` | Obligatorio con `DJANGO_DEBUG=0`: cadena aleatoria ≥40 caracteres (`openssl rand -base64 48`). |
| `DJANGO_DEBUG` | `0` en producción. |
| `DJANGO_ALLOWED_HOSTS` | Host público, p. ej. `tu-app.onrender.com`. |
| `DATABASE_URL` | Inyectada al enlazar PostgreSQL (o pegar Internal URL solo en el panel). |
| `GEMINI_API_KEY` | Para el botón de análisis IA en Reportes ([Google AI Studio](https://aistudio.google.com/apikey)). |
| `GEMINI_MODEL` | Opcional (p. ej. `gemini-2.0-flash`). |
| `GEMINI_MODEL_FALLBACKS` | Opcional: modelos alternativos separados por coma. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP para correo de recuperación de contraseña. |
| `DJANGO_DEFAULT_FROM_EMAIL` | Remitente del correo. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Opcional: `https://tu-app.onrender.com` (si no, se usa `RENDER_EXTERNAL_HOSTNAME` cuando aplica). |

### Después del primer deploy

- **Shell** del servicio: `python crear_admin.py` (una vez, si necesita usuarios iniciales) o `python manage.py seed_demo` solo en entornos de prueba.

### Archivos subidos (media)

En el plan típico de Render el disco del contenedor es **efímero**. Para conservar PDF/imágenes entre reinicios use un **Render Disk** en `MEDIA_ROOT` o almacenamiento externo (S3, etc.).

---

## Estructura relevante del repositorio

| Ruta | Contenido |
|------|-----------|
| `incasoft/` | Proyecto Django (`settings.py`, `urls.py`, `wsgi.py`). |
| `gestion/` | App principal: modelos, vistas, formularios, plantillas, estáticos, permisos, Gemini, validación de archivos. |
| `manage.py` | CLI de Django. |
| `requirements.txt` | Dependencias versionadas. |
| `build.sh` | Script de build para Render/CI. |
| `Procfile` | Comandos `release` y `web` para Render/Heroku. |
| `render.yaml` | Blueprint de ejemplo (ajustar nombres y secretos `sync: false`). |
| `crear_admin.py` | Creación opcional de usuarios por defecto (ejecutar en Shell, no en build). |
| `.env.example` | Documentación de variables (copiar a `.env` local; no subir `.env`). |

---

## Comprobación local tipo producción

```bash
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
export DATABASE_URL=postgresql://usuario:clave@host:5432/base
export RENDER=true
python manage.py check
```

Si la clave es insegura o se usa SQLite en combinación `RENDER`+producción, `check` / arranque fallarán con mensaje explícito según `settings.py`.

---

## Licencia y uso

Uso interno / académico según el contexto de su organización. Ajuste licencia y datos sensibles según su política.
