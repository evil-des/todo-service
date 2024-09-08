from rest_framework import viewsets
from apps.tags.models import Tag
from .serializers import TagSerializer
from api.permissions import IsAuthenticatedOrInternalService


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrInternalService]
