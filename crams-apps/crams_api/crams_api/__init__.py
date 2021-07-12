from .celery import app as celery_app

default_app_config = 'crams_api.apps.CramsAPIConfig'

__all__ = ['celery_app']
