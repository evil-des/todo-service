from django.db import models
from apps.tags.models import Tag
from apps.users.models import TelegramUser


class Task(models.Model):
    class Meta:
        db_table = "tasks"
        indexes = [
            models.Index(fields=["notify_status", "remind_time"]),
        ]

    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default=None)
    remind_time = models.DateTimeField(null=True, blank=True, default=None)
    notify_status = models.CharField(
        max_length=16,
        choices=[("pending", "pending"), ("enqueued", "enqueued"),
                 ("sent", "sent"), ("failed", "failed")],
        default="pending",
    )
    notify_attempts = models.PositiveIntegerField(default=0)
    last_enqueued_at = models.DateTimeField(null=True, blank=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    telegram_user = models.ForeignKey(
        TelegramUser,
        related_name="tasks",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    date_created = models.DateTimeField(auto_now_add=True)
