import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crams_notification.settings')

app = Celery('crams_notification')

# set the timezone
app.conf.timezone = settings.TIME_ZONE

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
