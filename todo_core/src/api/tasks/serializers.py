from rest_framework import serializers
from apps.tasks.models import Task
from api.tags.serializers import TagSerializer
from api.users.serializers import TelegramUserSerializer


class TaskSerializer(serializers.ModelSerializer):
    telegram_user = TelegramUserSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Task
        fields = '__all__'
