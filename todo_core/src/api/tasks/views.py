import json

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets
from rest_framework.response import Response
from apps.tasks.models import Task
from .serializers import TaskSerializer
from api.permissions import IsAuthenticatedOrInternalService
from api.utils import str_to_bool


class TaskViewSet(viewsets.ModelViewSet):
    queryset = (Task.objects.select_related('telegram_user').
                prefetch_related('tags').all())
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrInternalService]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'completed',
            openapi.IN_QUERY,
            description="Filter tasks by completion status",
            type=openapi.TYPE_BOOLEAN, required=False
        ),
        openapi.Parameter(
            'telegram_chat_id',
            openapi.IN_QUERY,
            description="Filter tasks by Telegram User' chat_id",
            type=openapi.TYPE_INTEGER, required=False
        ),
        openapi.Parameter(
            'tags_ids',
            openapi.IN_QUERY,
            description="Filter tasks by Tags IDs",
            type=openapi.TYPE_ARRAY, required=False,
            items=openapi.Items(type=openapi.TYPE_INTEGER)
        ),
    ])
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        q = request.query_params

        if q.get('completed'):
            queryset = queryset.filter(completed=str_to_bool(q.get('completed')))
        if q.get('telegram_chat_id'):
            queryset = queryset.filter(telegram_user__chat_id=q.get('telegram_chat_id'))
        if q.get('tags_ids'):
            queryset = queryset.filter(tags__id__in=q.get('tags_ids').split(","))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
