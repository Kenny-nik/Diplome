from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from apps.users.models import User
from apps.users.serializers import UserCreateSerializer
from rest_framework import status
from django.contrib import messages

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('book_list')
        form = AuthenticationForm()
        return render(request, 'authentication/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('book_list')
        else:
            messages.error(request, "Invalid email or password")
            return render(request, 'authentication/login.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('book_list')
        return render(request, 'authentication/register.html')

    def post(self, request):
        serializer = UserCreateSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect('book_list')
        else:
            # Передаем ошибки в шаблон
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'authentication/register.html')