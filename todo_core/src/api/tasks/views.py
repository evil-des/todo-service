from rest_framework import viewsets
from apps.tasks.models import Task
from .serializers import TaskSerializer
from api.permissions import IsAuthenticatedOrInternalService


class TaskViewSet(viewsets.ModelViewSet):
    queryset = (Task.objects.select_related('telegram_user').
                prefetch_related('tags').all())
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrInternalService]
