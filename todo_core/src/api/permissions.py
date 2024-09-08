from rest_framework.permissions import BasePermission


class IsAuthenticatedOrInternalService(BasePermission):
    def has_permission(self, request, view):
        services = ["bot", "comments:8000", "todo-core:8000"]
        print(request.META.get("HTTP_HOST"))

        if request.META.get("HTTP_HOST") in services:
            return True

        return request.user and request.user.is_authenticated
