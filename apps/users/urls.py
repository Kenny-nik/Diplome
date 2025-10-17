from django.urls import path
from . import views
from .views import ProfileView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('complete-profile/', views.CompleteProfileView.as_view(), name='complete_profile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('users/<int:pk>/', ProfileView.as_view(), name='profile'),
]