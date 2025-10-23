from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView


class SubscribeView(LoginRequiredMixin, TemplateView):
    """
    Фейковая оплата: ничего не списывает, просто продлевает подписку.
    GET — показывает форму, POST — «оформляет» подписку на N месяцев.
    """
    template_name = "users/subscribe.html"

    def post(self, request, *args, **kwargs):
        months = 1
        try:
            months = max(1, min(24, int(request.POST.get("months", "1") or 1)))
        except Exception:
            months = 1

        prof = request.user.profile
        today = date.today()

        start = prof.subscription_until if prof.subscription_until and prof.subscription_until >= today else today
        prof.subscription_until = start + timedelta(days=30 * months)
        prof.save(update_fields=["subscription_until"])

        messages.success(
            request,
            f"Подписка активна до {prof.subscription_until.strftime('%d.%m.%Y')}. Спасибо за поддержку!"
        )
        return redirect("users:subscribe_success")


class SubscribeSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "users/subscribe_success.html"
