from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from .forms import (
    AvatarForm,
    CustomUserCreationForm,
    ProfileForm,
    StyledPasswordChangeForm as PasswordChangeForm,
)
from .models import Profile


class RegisterView(View):
    """
    Регистрация нового пользователя.
    - Если пользователь уже авторизован — отправляем в профиль.
    - При успешной регистрации логиним и ведём на "дозаполнение" профиля.
    """
    template_name = "registration/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("profile")
        form = CustomUserCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("profile")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            # Если у тебя есть маршрут на «дозаполнение» — оставляем его.
            # Иначе можно заменить на: return redirect("profile")
            return redirect("complete_profile")
        # Ошибки валидации вернём на ту же страницу
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
