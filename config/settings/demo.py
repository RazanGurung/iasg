"""Public client-demo settings.

Same idea as dev.py — no restored SQL Server copy exists, so this runs on a
local SQLite file — but hardened enough to sit on the open internet: DEBUG is
off, WhiteNoise serves static files (no separate web server to configure),
and ALLOWED_HOSTS/SECRET_KEY come from the host's environment instead of the
committed .env fallback. Never used by the real app or by local dev.
"""
import os

from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "demo.sqlite3"},
    "legacy": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "demo.sqlite3"},
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
