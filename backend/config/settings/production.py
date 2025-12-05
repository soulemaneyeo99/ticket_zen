"""
Settings pour l'environnement de production
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='ticket-zen.onrender.com,*.onrender.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# CORS Configuration for production
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://ticket-zen.onrender.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# CSRF Configuration for production
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://ticket-zen.onrender.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

import dj_database_url

# Production database (keep PostgreSQL config from base.py)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Logging for production
# Use default file path from base.py (BASE_DIR / 'logs' / 'ticketzen.log')
# LOGGING['handlers']['file']['filename'] = '/var/log/ticketzen/ticketzen.log'