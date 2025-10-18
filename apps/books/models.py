from django.db import models
from django.conf import settings


class Book(models.Model):
    BOOK_GENRES = [
        ("FICTION", "Fiction"),
        ("SCI_FI", "Science Fiction"),
        ("MYSTERY", "Mystery"),
        ("ROMANCE", "Romance"),
        ("HISTORY", "History"),
        ("SCIENCE", "Science"),
        ("TECH", "Technology"),
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

    cover_url = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=3.5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_books",
    )

    class Meta:
        db_table = "books"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
            models.Index(fields=["genre"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"
