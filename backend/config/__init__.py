"""
Configuration du projet Ticket Zen
"""
# Importer Celery pour que Django le trouve
from .celery import app as celery_app

__all__ = ('celery_app',)