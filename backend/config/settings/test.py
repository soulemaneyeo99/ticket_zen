"""
Settings pour les tests
"""
from .base import *

DEBUG = False

# Base de données en mémoire pour les tests
import os

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


# Désactiver les migrations pour les tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Cache simple pour les tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Password hashers plus rapides pour les tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Désactiver le rate limiting pour les tests
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []

# Email backend pour tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery en mode eager pour les tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True