from django import template

register = template.Library()

@register.filter
def is_librarian(user):
    """True если пользователь библиотекарь (поле is_librarian, группа «Библиотекарь» или staff)."""
    try:
        if getattr(user, "is_librarian", False):
            return True
        if user.is_staff:
            return True
        return user.groups.filter(name="Библиотекарь").exists()
    except Exception:
        return False