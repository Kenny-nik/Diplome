from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Book(models.Model):
    BOOK_GENRES = [
        ('FICTION', 'Fiction'),
        ('SCI_FI', 'Science Fiction'),
        ('MYSTERY', 'Mystery'),
        ('ROMANCE', 'Romance'),
        ('HISTORY', 'History'),
        ('SCIENCE', 'Science'),
        ('TECH', 'Technology'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    publication_year = models.IntegerField()
    genre = models.CharField(max_length=50, choices=BOOK_GENRES)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'books'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['genre']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    loan_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)