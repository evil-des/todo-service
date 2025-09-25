from celery import Celery
from app.utils.get_settings import get_settings

settings = get_settings()

celery_app = Celery("bot")
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_default_queue=settings.CELERY_QUEUE,
    timezone=settings.CELERY_TIMEZONE,
)

celery_app.autodiscover_tasks(["app"])

import app.services.notifications.tasks  # noqa: F401
