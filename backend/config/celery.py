"""
Configuration Celery pour Ticket Zen
"""
import os
from celery import Celery
from django.conf import settings

# Définir le module de settings Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('ticket_zen')

# Utiliser les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tasks dans les apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """Task de debug"""
    print(f'Request: {self.request!r}')