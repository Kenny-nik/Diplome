from datetime import date
from django.utils import timezone

def user_has_premium(user) -> bool:
    """
    Универсальная проверка подписки для шаблонов и вьюх.
    Работает и с полем даты (subscription_until), и с булевым флагом (has_active_subscription).
    """
    if not getattr(user, "is_authenticated", False):
        return False

    profile = getattr(user, "profile", None)
    if not profile:
        return False

    # Вариант 1: дата до которой активна подписка
    until = getattr(profile, "subscription_until", None)
    if until:
        today = timezone.localdate()
        try:
            # Если в until вдруг DateTime — приводим к дате
            if hasattr(until, "date"):
                return until.date() >= today
            # Если это уже date
            return until >= today
        except Exception:
            pass

    # Вариант 2: простой булев флаг
    flag = getattr(profile, "has_active_subscription", None)
    if isinstance(flag, bool):
        return flag

    return False
