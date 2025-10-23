from .utils import user_has_premium

def subscription(request):
    """
    Кладём в контекст:
    - has_premium: True/False
    - subscription_until: если поле есть, отдадим как есть (может пригодиться в UI)
    """
    user = getattr(request, "user", None)
    ctx = {"has_premium": False, "subscription_until": None}
    if getattr(user, "is_authenticated", False):
        ctx["has_premium"] = user_has_premium(user)
        profile = getattr(user, "profile", None)
        if profile and hasattr(profile, "subscription_until"):
            ctx["subscription_until"] = getattr(profile, "subscription_until", None)
    return ctx
