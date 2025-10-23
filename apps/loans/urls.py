from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API URLs
router = DefaultRouter()
router.register('loans', views.LoanViewSet, basename='loan')

api_urlpatterns = [
    path('', include(router.urls)),
]

# Web URLs
urlpatterns = [
    path('api/', include(api_urlpatterns)),
]