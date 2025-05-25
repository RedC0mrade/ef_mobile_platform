from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from django.views.generic.edit import CreateView

class UserAccesMixin(AccessMixin):
    """Миксин проверки прав пользователя"""
    user_field = 'user'
    permission_denied_message = "У вас нет прав для редактирования этого объекта"

    def dispatch(self, request, *args, **kwargs):
        # Не делаем проверку, если это CreateView (объекта ещё нет)
        if isinstance(self, CreateView):
            return super().dispatch(request, *args, **kwargs)

        obj = self.get_object()
        user = getattr(obj, self.user_field)

        if user != request.user:
            if self.raise_exception:
                raise PermissionDenied(self.permission_denied_message)
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
