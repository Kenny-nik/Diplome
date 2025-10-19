from django.urls import path
from . import views

app_name = "librarian"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("users/", views.UsersListView.as_view(), name="users"),
    path("loans/", views.LoansListView.as_view(), name="loans"),
]
