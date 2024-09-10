from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from drf_yasg import openapi
from apps.users.models import User, TelegramUser
from .serializers import UserSerializer, TelegramUserSerializer
from api.permissions import IsAuthenticatedOrInternalService
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('telegram_user').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrInternalService]


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticatedOrInternalService]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'chat_id',
            openapi.IN_QUERY,
            description="Filter tasks by Telegram User' chat_id",
            type=openapi.TYPE_INTEGER, required=False
        ),
    ])
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        q = request.query_params

        serializer = self.get_serializer(queryset, many=True)

        if q.get('chat_id'):
            queryset = TelegramUser.objects.filter(chat_id=q.get('chat_id')).first()
            serializer = self.get_serializer(queryset, many=False)

        return Response(serializer.data)
