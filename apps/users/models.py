from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('READER', 'Reader'),
        ('LIBRARIAN', 'Librarian'),
        ('ADMIN', 'Administrator'),
    ]

    # поля, которых не было в стандартном пользователе
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='READER')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_librarian(self):
        return self.role in ['LIBRARIAN', 'ADMIN']

    @property
    def is_admin(self):
        return self.role == 'ADMIN'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)