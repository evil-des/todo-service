from rest_framework.permissions import BasePermission


class IsAuthenticatedOrInternalService(BasePermission):
    def has_permission(self, request, view):
        services = ["bot", "comments"]

        if request.META.get("REMOTE_ADDR") in services:
            return True

        return request.user and request.user.is_authenticated
