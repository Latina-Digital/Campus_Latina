"""
Configuración de Campus Latina.

Los valores sensibles se leen de variables de entorno o del archivo `.env`
(ver `.env.example`). Los valores por defecto sirven para desarrollo local.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env(name, default=None):
    return os.getenv(name, default)


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-solo-local-cambiar-en-produccion-campus-latina")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "*")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Apps del campus
    "apps.core",
    "apps.accounts",
    "apps.catalog",
    "apps.courses",
    "apps.assessments",
    "apps.certificates",
    "apps.panel",
    "apps.apidata",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.campus",
            ],
            "builtins": ["apps.core.templatetags.campus"],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Los datos del campus viven en SQL Server y se leen y escriben por la API
# (CAMPUS_API_URL, ver apps/apidata). Esta base SQLite es solo la copia de trabajo:
# se vuelve a llenar desde la API cada vez que arranca el sitio. Guarda además las
# sesiones abiertas.
SQLITE_PATH = BASE_DIR / env("SQLITE_PATH", "data/copia_api.sqlite3")
SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SQLITE_PATH,
        # Espera en lugar de fallar si otra petición está escribiendo.
        "OPTIONS": {"timeout": 20, "transaction_mode": "IMMEDIATE"},
    }
}

AUTH_USER_MODEL = "accounts.User"
# Los usuarios son los de Syspro: no hay cuentas propias del campus.
AUTHENTICATION_BACKENDS = ["apps.accounts.backends.SysproBackend"]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
]
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "courses:home"
LOGOUT_REDIRECT_URL = "core:landing"

LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}
# Sirve /media/ desde Django (con soporte de rangos para videos). Desactivar si un
# servidor web (IIS, Nginx) se encarga de los archivos subidos.
SERVE_MEDIA = env_bool("SERVE_MEDIA", True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

SESSION_COOKIE_AGE = 60 * 60 * 10  # 10 horas
MESSAGE_TAGS = {10: "info", 20: "info", 25: "success", 30: "warning", 40: "error"}

# --- Publicación -------------------------------------------------------------
# HTTPS=True cuando IIS sirve el sitio con certificado SSL. IIS hace la redirección
# de http a https; Waitress recibe la petición ya descifrada (ver serve.py).
HTTPS = env_bool("HTTPS", False)
if not DEBUG:
    SESSION_COOKIE_SECURE = HTTPS
    CSRF_COOKIE_SECURE = HTTPS
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "SAMEORIGIN"
    if HTTPS:
        SECURE_HSTS_SECONDS = int(env("HSTS_SECONDS", "0"))

# Bloqueo temporal tras varios intentos fallidos de inicio de sesión.
LOGIN_MAX_ATTEMPTS = int(env("LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_LOCKOUT_MINUTES = int(env("LOGIN_LOCKOUT_MINUTES", "15"))

# --- Integración opcional con el login corporativo (Syspro) -----------------
# Si está activo, un usuario que no exista en el campus se valida contra la API
# y se crea automáticamente con su nombre, rol y supervisor.
SYSPRO_ENABLED = env_bool("SYSPRO_ENABLED", False)
SYSPRO_API_URL = env("SYSPRO_API_URL", "")
# URLs adicionales separadas por coma: se prueban en orden si la anterior no responde.
SYSPRO_API_URLS = env_list("SYSPRO_API_URLS", "")
SYSPRO_API_KEY = env("SYSPRO_API_KEY", "")
SYSPRO_TIMEOUT = int(env("SYSPRO_TIMEOUT", "5"))
SYSPRO_ADMIN_USERS = [u.lower() for u in env_list("SYSPRO_ADMIN_USERS", "")]

# --- Datos del campus (API) ---------------------------------------------------
# Endpoint api/syspro/campus/datos. Sin URL, el campus trabaja solo con la base
# local (desarrollo y pruebas automáticas).
CAMPUS_API_URL = env("CAMPUS_API_URL", "")
CAMPUS_API_URLS = env_list("CAMPUS_API_URLS", "")
CAMPUS_API_KEY = env("CAMPUS_API_KEY", "") or SYSPRO_API_KEY
CAMPUS_API_TIMEOUT = int(env("CAMPUS_API_TIMEOUT", "20"))
if sys.argv[1:2] == ["test"]:
    # Las pruebas nunca escriben en la API real.
    CAMPUS_API_URL, CAMPUS_API_URLS = "", []

# --- Identidad del campus ----------------------------------------------------
CAMPUS_NAME = env("CAMPUS_NAME", "Campus Latina")
CAMPUS_COMPANY = env("CAMPUS_COMPANY", "Industrial Latina S.A.")
CAMPUS_SIGNER_1 = env("CAMPUS_SIGNER_1", "Gerencia Comercial")
CAMPUS_SIGNER_2 = env("CAMPUS_SIGNER_2", "Jefatura de Capacitación")
# URL pública usada en el QR de los certificados (ej: https://campus.latina.com.ec).
# Si se deja vacía se usa la dirección desde la que se generó el certificado.
CAMPUS_PUBLIC_URL = env("CAMPUS_PUBLIC_URL", "").rstrip("/")

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "campus.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "plain",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "apps": {"handlers": ["console", "file"], "level": "INFO"},
        "django.request": {"handlers": ["file"], "level": "ERROR"},
    },
}
