"""Shared settings. Environment-specific values live in dev.py / prod.py."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Windows dev convenience: make WeasyPrint's native GTK/Pango/Cairo libs
# discoverable. WeasyPrint calls os.add_dll_directory() for each entry in
# WEASYPRINT_DLL_DIRECTORIES itself, but that alone isn't always enough —
# cffi's dlopen fallback needs the same directories on PATH too, ahead of
# any conflicting bundled copy elsewhere (e.g. Tesseract-OCR ships its own,
# incompatible libgobject-2.0-0.dll). No-op on Linux / if unset.
if hasattr(os, "add_dll_directory"):
    for _dll_dir in os.environ.get("WEASYPRINT_DLL_DIRECTORIES", "").split(";"):
        if _dll_dir and os.path.isdir(_dll_dir):
            os.environ["PATH"] = _dll_dir + os.pathsep + os.environ["PATH"]
            os.add_dll_directory(_dll_dir)

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "apps.core",
    "apps.clients",
    "apps.salestax",
    "apps.banking",
    "apps.financials",
    "apps.worklists",
    "apps.comms",
    "apps.ach",
    "apps.reports",
    "apps.security",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    # records who viewed which protected fields — see docs/security.md
    "apps.security.middleware.AuditMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

# ---------------------------------------------------------------------------
# Database
#
# One SQL Server instance, two logical roles:
#   default  - Django's own tables (auth, sessions, audit) in the app schema
#   legacy   - the existing Access-era tables. Models are managed = False.
#
# On the app server this is a LOCAL connection: SQL Server is on the same box.
# ---------------------------------------------------------------------------
_MSSQL = {
    "ENGINE": "mssql",
    "NAME": os.environ["DB_NAME"],
    "HOST": os.environ.get("DB_HOST", "localhost"),
    "PORT": os.environ.get("DB_PORT", "1433"),
    "USER": os.environ.get("DB_USER", ""),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "OPTIONS": {
        "driver": os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
        # Driver 18 defaults to Encrypt=yes and rejects untrusted certs.
        "extra_params": f"TrustServerCertificate={os.environ.get('DB_TRUST_CERT', 'yes')}",
    },
}
DATABASES = {"default": _MSSQL, "legacy": {**_MSSQL}}
DATABASE_ROUTERS = ["config.routers.LegacyRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 9

# Keys are read from the environment and MUST NOT be stored in the database.
FIELD_ENCRYPTION_KEY = os.environ.get("FIELD_ENCRYPTION_KEY", "")
CREDENTIAL_VAULT_KEY = os.environ.get("CREDENTIAL_VAULT_KEY", "")
