from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TelegramUser


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_active', 'telegram_user')
    search_fields = ('username', 'first_name', 'last_name', 'telegram_user')
    list_filter = ('is_active', 'telegram_user')
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'telegram_user')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'telegram_user')
        })
    )

    ordering = ['username']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'last_name')
