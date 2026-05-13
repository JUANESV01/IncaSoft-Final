import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on', 'si'}


def env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


load_env_file(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Render y otros hosts suelen definir SECRET_KEY o DJANGO_SECRET_KEY.
SECRET_KEY = (
    os.environ.get('DJANGO_SECRET_KEY', '').strip()
    or os.environ.get('SECRET_KEY', '').strip()
    or 'django-insecure-*j6hy_b)rx^bvn_=toa+%wuc3%r$+hldofu#o-tu0z)u81%(2%'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DJANGO_DEBUG', True)

# Render.com define RENDER=true y RENDER_EXTERNAL_HOSTNAME
RENDER = env_bool('RENDER', False)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1],testserver').split(',')
    if host.strip()
]
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, RENDER_EXTERNAL_HOSTNAME]

# CSRF: obligatorio en HTTPS (login, recuperación de contraseña, fetch con cookies)
_csrf_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').strip()
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]
elif RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']
else:
    CSRF_TRUSTED_ORIGINS = []


# Application definition

INSTALLED_APPS = [
    'gestion',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'incasoft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'gestion.context_processors.permisos_ui',
            ],
        },
    },
]

WSGI_APPLICATION = 'incasoft.wsgi.application'


# Database: DATABASE_URL (Render, Heroku, etc.) tiene prioridad sobre DB_* / SQLite.
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()

if DATABASE_URL:
    import dj_database_url

    _db_ssl_default = bool(
        DATABASE_URL
        and (
            'render.com' in DATABASE_URL
            or 'amazonaws.com' in DATABASE_URL
            or 'sslmode=require' in DATABASE_URL
        )
    )
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=env_int('DB_CONN_MAX_AGE', 600),
            conn_health_checks=True,
            ssl_require=env_bool('DATABASE_SSL_REQUIRE', _db_ssl_default),
        )
    }
else:
    DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite').lower()

    if DB_ENGINE in {'postgres', 'postgresql'}:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME', 'incasoft_db'),
                'USER': os.environ.get('DB_USER', 'incasoft_user'),
                'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
                'PORT': os.environ.get('DB_PORT', '5432'),
                'CONN_MAX_AGE': env_int('DB_CONN_MAX_AGE', 60),
                'CONN_HEALTH_CHECKS': env_bool('DB_CONN_HEALTH_CHECKS', True),
                'OPTIONS': {
                    'connect_timeout': env_int('DB_CONNECT_TIMEOUT', 10),
                    'application_name': os.environ.get('DB_APPLICATION_NAME', 'incasoft_solutions'),
                    'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),
                    'options': os.environ.get('DB_SESSION_OPTIONS', '-c timezone=America/Bogota'),
                },
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'gestion:dashboard'
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Correo (recuperación de contraseña, notificaciones) ─────────────────────
# Si define EMAIL_HOST, se usa SMTP salvo que fuerce otro backend con DJANGO_EMAIL_BACKEND.
EMAIL_HOST = os.environ.get('EMAIL_HOST', '').strip()
EMAIL_PORT = env_int('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
EMAIL_TIMEOUT = env_int('EMAIL_TIMEOUT', 25)

if EMAIL_HOST:
    EMAIL_BACKEND = os.environ.get(
        'DJANGO_EMAIL_BACKEND',
        'django.core.mail.backends.smtp.EmailBackend',
    )
else:
    EMAIL_BACKEND = os.environ.get(
        'DJANGO_EMAIL_BACKEND',
        'django.core.mail.backends.console.EmailBackend',
    )

DEFAULT_FROM_EMAIL = os.environ.get(
    'DJANGO_DEFAULT_FROM_EMAIL',
    EMAIL_HOST_USER or 'no-reply@incasoft.local',
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Enlace absoluto en correos de recuperación
SITE_NAME = os.environ.get('DJANGO_SITE_NAME', 'INCASOFT Solutions')
PASSWORD_RESET_TIMEOUT = env_int('DJANGO_PASSWORD_RESET_TIMEOUT', 60 * 60 * 24 * 3)  # 3 días

# Google Gemini (reportes — análisis con IA). Clave desde https://aistudio.google.com/apikey
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash').strip() or 'gemini-2.0-flash'
# Modelos alternativos si el principal no está disponible en su región/cuenta (coma separada)
_gemini_fb = os.environ.get('GEMINI_MODEL_FALLBACKS', 'gemini-2.5-flash,gemini-1.5-flash').strip()
GEMINI_MODEL_FALLBACKS = tuple(m.strip() for m in _gemini_fb.split(',') if m.strip())
GEMINI_MAX_RETRIES = env_int('GEMINI_MAX_RETRIES', 2)

# --- Producción (HTTPS detrás de proxy, cookies seguras) ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    if env_bool('DJANGO_SECURE_SSL_REDIRECT', True):
        SECURE_SSL_REDIRECT = True

# Validación estricta en Render + producción.
# Se omite solo durante collectstatic/findstatic (build en Render puede correr antes de pegar SECRET_KEY).
def _collectstatic_or_findstatic_argv() -> bool:
    argv = getattr(sys, "argv", [])
    for i, arg in enumerate(argv):
        if os.path.basename(arg).lower() == "manage.py" and i + 1 < len(argv):
            return argv[i + 1] in ("collectstatic", "findstatic")
    return False


def _render_strict_validation() -> bool:
    if not (RENDER and not DEBUG):
        return False
    if _collectstatic_or_findstatic_argv():
        return False
    return True


# Validación mínima en despliegue Render sin DEBUG
if _render_strict_validation():
    _sk_env = bool(os.environ.get('DJANGO_SECRET_KEY', '').strip() or os.environ.get('SECRET_KEY', '').strip())
    if not _sk_env or 'django-insecure' in SECRET_KEY or len(SECRET_KEY) < 40:
        raise ImproperlyConfigured(
            'En Render con DJANGO_DEBUG=0 debe definir una clave secreta en el panel Environment: '
            'DJANGO_SECRET_KEY o SECRET_KEY (mínimo 40 caracteres aleatorios). '
            'Ejemplo en su máquina: openssl rand -base64 48'
        )
    _db_engine = DATABASES['default'].get('ENGINE', '')
    if 'sqlite' in _db_engine:
        raise ImproperlyConfigured(
            'En Render debe usar PostgreSQL (no SQLite). En el Web Service: Connect → Link database '
            'y elija su instancia existente (p. ej. incasoft-db) para que exista DATABASE_URL, '
            'o defina DATABASE_URL con la Internal Database URL de esa base.'
        )

# Logging (para ver errores 500 en Render)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
