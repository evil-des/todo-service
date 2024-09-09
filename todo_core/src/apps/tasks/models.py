from django.db import models
from apps.tags.models import Tag
from apps.users.models import TelegramUser


class Task(models.Model):
    class Meta:
        db_table = "tasks"

    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default=None)
    remind_time = models.DateTimeField(null=True, blank=True, default=None)
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    telegram_user = models.ForeignKey(
        TelegramUser,
        related_name="tasks",
        blank=True, null=True,
        on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(auto_now_add=True)
