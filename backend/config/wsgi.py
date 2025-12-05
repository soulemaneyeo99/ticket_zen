"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Respect DJANGO_SETTINGS_MODULE if already set (e.g., by start.sh)
# Otherwise, determine environment
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    environment = os.environ.get('DJANGO_ENV', 'development')
    
    if environment == 'production':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    elif environment == 'test':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
