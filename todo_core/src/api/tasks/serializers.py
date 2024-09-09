from rest_framework import serializers
from apps.tasks.models import Task
from api.tags.serializers import TagSerializer
from api.users.serializers import TelegramUserSerializer


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        add_fields = kwargs.pop('add_fields', None)
        super().__init__(*args, **kwargs)

        if add_fields:
            if 'telegram_user' in add_fields:
                self.fields['telegram_user'] = TelegramUserSerializer()
            if 'tags' in add_fields:
                self.fields['tags'] = TagSerializer(many=True)
