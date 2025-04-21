import os
from celery import Celery

# Set default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Load custom config from Django settings (CELERY_ prefix)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks across all registered apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
