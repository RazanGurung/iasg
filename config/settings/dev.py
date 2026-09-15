from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# No restored copy of the legacy SQL Server database exists yet (see
# docs/open-questions.md). Develop against local SQLite instead until then —
# swap back to the real mssql config already built in base.py once it does.
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "dev.sqlite3"},
    "legacy": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "dev.sqlite3"},
}
