import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datapusher.settings')

app = Celery('datapusher')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()