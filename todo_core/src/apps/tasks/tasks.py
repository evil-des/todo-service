from celery import shared_task, current_app
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from apps.tasks.models import Task


@shared_task
def enqueue_todos():
    now = timezone.now()
    window = now + timedelta(seconds=5)
    batch_size = 200

    while True:
        with transaction.atomic():
            qs = (Task.objects
                  .select_for_update(skip_locked=True)
                  .filter(notify_status__in=["pending", "failed"], remind_time__lte=window)
                  .order_by("remind_time")[:batch_size])
            items = list(qs)
            if not items:
                break

            for t in items:
                t.notify_status = "enqueued"
                t.save(update_fields=["notify_status"])

                current_app.send_task(
                    "send_telegram",
                    kwargs={
                        "chat_id": t.telegram_user.chat_id,
                        "text": t.title,
                        "task_id": t.id,
                    },
                    queue="notifications",
                )


@shared_task(name="send_telegram")
def send_telegram_stub(*_, **__):
    # Реализация будет в бот-репозитории/сервисе
    return True
