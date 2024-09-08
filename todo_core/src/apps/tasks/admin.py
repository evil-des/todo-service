from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'completed', 'remind_time', 'telegram_user_chat_id', 'date_created')
    search_fields = ('title', 'completed', 'remind_time', 'tags', 'telegram_user_chat_id', 'date_created')
    list_filter = ('completed', 'telegram_user', 'tags')

    ordering = ['date_created']

    def telegram_user_chat_id(self, obj):
        return obj.telegram_user.chat_id
