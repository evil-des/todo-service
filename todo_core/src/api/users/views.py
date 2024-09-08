from rest_framework import viewsets
from apps.users.models import User, TelegramUser
from .serializers import UserSerializer, TelegramUserSerializer
from api.permissions import IsAuthenticatedOrInternalService


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('telegram_user').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrInternalService]


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticatedOrInternalService]
