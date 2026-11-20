from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.groups.filter(name='moderators').exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsNotModer(BasePermission):
    """Разрешение только для тех, кто НЕ состоит в группе moderators."""
    message = 'Модераторы не могут создавать материалы.'

    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()
