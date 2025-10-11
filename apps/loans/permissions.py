from rest_framework import permissions


class IsOwnerOrLibrarian(permissions.BasePermission):
    """
    Разрешение, позволяющее владельцу займа или библиотекарю получать доступ.
    """

    def has_object_permission(self, request, view, obj):
        # Библиотекари имеют полный доступ
        if request.user.is_librarian:
            return True

        # Пользователи могут видеть только свои займы
        return obj.user == request.user