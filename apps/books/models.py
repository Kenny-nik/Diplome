from django.db import models
from django.utils.text import slugify

BOOK_GENRES = (
    ("FANTASY", "Фэнтези"),
    ("SCIFI", "Научная фантастика"),
    ("MYSTERY", "Детектив"),
    ("ROMANCE", "Роман"),
    ("TECH", "Технологии"),
    ("HISTORY", "История"),
    ("OTHER", "Другое"),
)


class Book(models.Model):
    GENRE_CHOICES = [
        ("sci_fi", "Научная фантастика"),
        ("romance", "Роман"),
        ("history", "История"),
        ("cs", "Программирование"),
        ("science", "Наука"),
        ("detective", "Детектив"),
        ("poetry", "Поэзия"),
        ("other", "Другое"),
    ]

    BOOK_GENRES = GENRE_CHOICES

    genre = models.CharField(
        "Жанр",
        max_length=32,
        choices=GENRE_CHOICES,
        default="other",
        blank=True,
    )
    title = models.CharField("Название", max_length=255)
    slug = models.SlugField("Слаг", max_length=255, unique=True, blank=True)
    author = models.CharField("Автор", max_length=255, blank=True)
    isbn = models.CharField("ISBN", max_length=32, blank=True)
    publication_year = models.PositiveIntegerField("Год издания", blank=True, null=True)

    genre = models.CharField("Жанр", max_length=20, choices=BOOK_GENRES, default="OTHER")
    description = models.TextField("Описание", blank=True)


    cover_url = models.URLField("URL обложки", blank=True, null=True)
    cover_image = models.ImageField("Файл обложки", upload_to="covers/", blank=True, null=True)

    rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=1, default=0)
    total_copies = models.PositiveIntegerField("Всего экземпляров", default=1)
    available_copies = models.PositiveIntegerField("Доступно", default=1)
    is_available = models.BooleanField("Доступна для выдачи", default=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self) -> str:
        return self.title

    @property
    def preferred_cover(self) -> str | None:
        """
        Приоритет обложки: загруженный файл → URL → None (шаблон покажет заглушку).
        """
        if self.cover_image:
            try:
                return self.cover_image.url
            except Exception:
                return None
        if self.cover_url:
            return self.cover_url
        return None

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.slug:
            base = slugify(self.title) or f"book-{self.pk}"
            slug = base
            i = 2
            from django.db.models import Q
            while Book.objects.filter(Q(slug=slug) & ~Q(pk=self.pk)).exists():
                slug = f"{base}-{i}"
                i += 1
            Book.objects.filter(pk=self.pk).update(slug=slug)
            self.slug = slug
