from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

from .forms import (
    AvatarForm,
    CustomUserCreationForm,
    ProfileForm,
    StyledPasswordChangeForm as PasswordChangeForm,
)
from .models import Profile


class RegisterView(View):
    template_name = "registration/register.html"

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вы успешно зарегистрированы!")
            return redirect("profile")
        messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
        return render(request, self.template_name, {"form": form})


class CompleteProfileView(LoginRequiredMixin, View):
    """
    Небольшой шаг после регистрации: имя/фамилия и т.п.
    """
    template_name = "users/complete_profile.html"

    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль заполнен.")
            return redirect("profile")
        return render(request, self.template_name, {"form": form})


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Страница профиля: аватар, личные данные, смена пароля.
    """
    template_name = "users/profile.html"

    def _get_profile(self, user):
        # На случай если сигнал не сработал — создадим профиль здесь.
        return getattr(user, "profile", None) or Profile.objects.create(user=user)

    def get(self, request, *args, **kwargs):
        profile = self._get_profile(request.user)
        ctx = {
            "profile_form": ProfileForm(instance=request.user),
            "avatar_form": AvatarForm(instance=profile),
            "password_form": PasswordChangeForm(user=request.user),
        }
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "profile")
        profile = self._get_profile(request.user)

        if action == "profile":
            pf = ProfileForm(request.POST, instance=request.user)
            if pf.is_valid():
                pf.save()
                messages.success(request, "Профиль обновлён.")
                return redirect("profile")
            ctx = {
                "profile_form": pf,
                "avatar_form": AvatarForm(instance=profile),
                "password_form": PasswordChangeForm(user=request.user),
            }
            return render(request, self.template_name, ctx)

        if action == "avatar":
            af = AvatarForm(request.POST, request.FILES, instance=profile)
            if af.is_valid():
                af.save()
                messages.success(request, "Аватар обновлён.")
                return redirect("profile")
            ctx = {
                "profile_form": ProfileForm(instance=request.user),
                "avatar_form": af,
                "password_form": PasswordChangeForm(user=request.user),
            }
            return render(request, self.template_name, ctx)

        if action == "password":
            pwf = PasswordChangeForm(user=request.user, data=request.POST)
            if pwf.is_valid():
                pwf.save()
                # чтобы не разлогинило после смены пароля
                update_session_auth_hash(request, pwf.user)
                messages.success(request, "Пароль изменён.")
                return redirect("profile")
            ctx = {
                "profile_form": ProfileForm(instance=request.user),
                "avatar_form": AvatarForm(instance=profile),
                "password_form": pwf,
            }
            return render(request, self.template_name, ctx)

        return redirect("profile")

@login_required
def fake_checkout(request):
    """
    Заглушка оплаты. Никуда карты не отправляются.
    Просто активируем подписку на 30 дней и возвращаемся назад.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    profile = request.user.profile
    profile.subscription_until = timezone.localdate() + timedelta(days=30)
    profile.save(update_fields=["subscription_until"])

    messages.success(
        request,
        f"Подписка активирована до {profile.subscription_until.strftime('%d.%m.%Y')}. "
        f"Это тестовая оплата (без реального списания)."
    )

    next_url = request.POST.get("next") or reverse("home")
    return redirect(next_url)

@login_required
def subscribe_placeholder(request):
    """
    Демонстрационная заглушка оформления подписки.
    Реальной оплаты пока нет: показываем сообщение и отправляем в профиль.
    """
    messages.info(
        request,
        "Оплата подписки пока не подключена. Это демонстрационная кнопка. "
        "Для теста можете выдать подписку в админке (поле «Подписка до»)."
    )
    return redirect("users:profile")