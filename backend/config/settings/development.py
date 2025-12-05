"""
Settings pour l'environnement de développement
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1", "backend"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
]

# CORS more permissive in dev
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_ALL_ORIGINS = True

# Database pour développement
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "ticketzen_db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}
# CORS plus permissif en dev
CORS_ALLOW_ALL_ORIGINS = True

# Email backend console pour dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Cache simple en dev
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging plus verbeux
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'