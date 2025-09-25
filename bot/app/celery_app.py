from celery import Celery
from app.utils.get_settings import get_settings

settings = get_settings()

app = Celery("bot")
app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_default_queue=settings.CELERY_QUEUE,
    timezone=settings.CELERY_TIMEZONE,
)

app.autodiscover_tasks(["app"])
