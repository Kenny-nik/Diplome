from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Вход
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    # Выход
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    # Регистрация
    path("register/", views.RegisterView.as_view(), name="register"),
    # Профиль
    path("profile/", views.ProfileView.as_view(), name="profile"),

    # Подписка (заглушки)
    path("subscribe/fake-checkout/", views.fake_checkout, name="fake_checkout"),
    path("subscribe/", views.subscribe_placeholder, name="subscribe"),
]
