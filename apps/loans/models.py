from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.books.models import Book
from apps.users.models import User


class Loan(models.Model):
    LOAN_STATUS = [
        ('ACTIVE', 'Активен'),
        ('RETURNED', 'Возвращен'),
        ('OVERDUE', 'Просрочен'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        ordering = ['-loan_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Loan #{self.id} - {self.book.title}"

    def save(self, *args, **kwargs):
        # Автоматическое обновление статуса
        if self.return_date:
            self.status = 'RETURNED'
        elif self.due_date < timezone.now() and not self.return_date:
            self.status = 'OVERDUE'
        else:
            self.status = 'ACTIVE'

        super().save(*args, **kwargs)

    def mark_returned(self):
        """Пометить книгу как возвращенную"""
        self.return_date = timezone.now()
        self.status = 'RETURNED'

        # Обновляем доступность книги
        self.book.available_copies += 1
        if self.book.available_copies > 0:
            self.book.is_available = True
        self.book.save()

        self.save()

    @property
    def is_overdue(self):
        """Проверить, просрочен ли заем"""
        return self.due_date < timezone.now() and self.status == 'ACTIVE'

    @property
    def days_overdue(self):
        """Количество дней просрочки"""
        if self.is_overdue:
            return (timezone.now() - self.due_date).days
        return 0