from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцу объекта редактировать его.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsReceiver(permissions.BasePermission):
    """
    Разрешает доступ только получателю предложения обмена
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return obj.ad_receiver.user == request.user
