from django.contrib.auth.models import AbstractUser
from django.db import models


class TelegramUser(models.Model):
    class Meta:
        db_table = 'telegram_users'

    chat_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    last_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    username = models.CharField(max_length=255, null=True, blank=True, default=None)


class User(AbstractUser):
    class Meta:
        db_table = "users"

    telegram_user = models.OneToOneField(
        TelegramUser, on_delete=models.CASCADE,
        null=True, blank=True, default=None
    )
