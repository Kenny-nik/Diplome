from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from apps.users.views import RegisterView, ProfileView



urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # Apps
    path('books/', include('apps.books.urls')),
    path('loans/', include('apps.loans.urls')),
    path('users/', include('apps.users.urls')),

    # API
    path('api/v1/', include([
        # path('auth/', include('apps.users.api_urls')),
        path('books/', include('apps.books.api_urls')),
        path('loans/', include('apps.loans.api_urls')),
    ])),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]