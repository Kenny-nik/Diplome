from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

def is_librarian(user) -> bool:
    """
    Доступ разрешён, если:
    - пользователь аутентифицирован и superuser, ИЛИ
    - is_staff = True, ИЛИ
    - состоит в группе 'Библиотекарь' (имя без учёта регистра).
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    try:
        return user.groups.filter(name__iexact="Библиотекарь").exists()
    except Exception:
        return False

class LibrarianRequiredMixin(UserPassesTestMixin):
    """Миксин для CBV: допускает только библиотекарей."""
    raise_exception = True  # чтобы получать 403, а не редирект на логин

    def test_func(self):
        return is_librarian(self.request.user)

    def handle_no_permission(self):
        # оставим стандартный PermissionDenied (403)
        raise PermissionDenied
