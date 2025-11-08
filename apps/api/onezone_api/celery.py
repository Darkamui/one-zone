import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onezone_api.settings')

app = Celery('onezone_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'create-version-snapshots-every-hour': {
        'task': 'bgtasks.page_tasks.create_version_snapshots',
        'schedule': crontab(minute=0),  # Every hour
    },
    'cleanup-old-versions-daily': {
        'task': 'bgtasks.page_tasks.cleanup_old_versions',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}