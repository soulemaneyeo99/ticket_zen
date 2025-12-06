"""
Settings pour l'environnement de production
"""
from .base import *
import sys

# Debug: confirm production settings are loaded
print("=" * 50, file=sys.stderr)
print("LOADING PRODUCTION SETTINGS", file=sys.stderr)
print("=" * 50, file=sys.stderr)

DEBUG = False

# ALLOWED_HOSTS with proper wildcard syntax (.domain.com not *.domain.com)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='ticket-zen.onrender.com,.onrender.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# CORS Configuration for production (remove trailing slashes)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://ticket-zen.onrender.com,https://ticket-zen-six.vercel.app',
    cast=lambda v: [s.strip().rstrip('/') for s in v.split(',')]
)

# CSRF Configuration for production
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://ticket-zen.onrender.com,https://ticket-zen-six.vercel.app',
    cast=lambda v: [s.strip().rstrip('/') for s in v.split(',')]
)

print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}", file=sys.stderr)
print(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}", file=sys.stderr)
print(f"CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}", file=sys.stderr)

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session and Cookie settings for API
# Since this is an API-first application, we don't need strict session cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-site requests for API

# CSRF settings for API
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript to read it
CSRF_COOKIE_SAMESITE = 'None'  # Allow cross-site requests
CSRF_USE_SESSIONS = False  # Use cookie-based CSRF instead of session

# HSTS settings (less strict for initial deployment)
SECURE_HSTS_SECONDS = 0  # Disable HSTS for now
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

import dj_database_url

# Production database configuration
# Try to use DATABASE_URL first (Render PostgreSQL addon)
# If not available, fall back to individual DB_* environment variables from base.py
database_url = config('DATABASE_URL', default='')

if database_url:
    # Use DATABASE_URL if provided (Render PostgreSQL addon)
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
    print(f"Using DATABASE_URL for database connection", file=sys.stderr)
else:
    # Fall back to base.py configuration with individual variables
    # DATABASES is already defined in base.py, just update connection settings
    DATABASES['default']['CONN_MAX_AGE'] = 600
    DATABASES['default']['OPTIONS']['connect_timeout'] = 10
    print(f"Using DB_* environment variables for database connection", file=sys.stderr)
    print(f"DB_HOST: {DATABASES['default']['HOST']}", file=sys.stderr)

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Cache Configuration for production (use local memory instead of Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging for production
# Use default file path from base.py (BASE_DIR / 'logs' / 'ticketzen.log')
# LOGGING['handlers']['file']['filename'] = '/var/log/ticketzen/ticketzen.log'