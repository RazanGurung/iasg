from .base import *  # noqa

DEBUG = False

# Behind IIS terminating TLS on the LAN.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",  # noqa: F405
            "maxBytes": 10_000_000,
            "backupCount": 10,
        },
    },
    # NOTE: never log protected field values. See docs/security.md.
    "root": {"handlers": ["file"], "level": "INFO"},
}
