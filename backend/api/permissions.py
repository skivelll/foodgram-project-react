from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """
    Permission с правом доступа только если роль пользователя
    администратор или супер пользоветель.
    """

    message = 'Только администратор может выполнять это действие!'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_staff
        )


class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Permission с правом доступа только если это безопасный запрос,
    или пользователь является администратором.
    """

    def has_permission(self, request, view):
        return (((request.method in SAFE_METHODS) or request.user.is_staff)
                or MethodNotAllowed)


class IsAuthorOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return ((obj.author == request.user or request.user.is_staff)
                and request.user.is_authenticated)


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """
    Permission с правом доступа только если это безопасный запрос,
    или пользователь является автором получаемого объекта.
    """

    message = 'Изменять чужие данные нельзя!'

    def has_permission(self, request, view):
        return ((request.method in SAFE_METHODS)
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (((request.method == 'POST'
                  or obj.author == request.user or request.user.is_staff)
                 and request.user.is_authenticated)
                or request.method in SAFE_METHODS)
