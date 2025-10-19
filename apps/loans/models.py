from django.db import models
from django.conf import settings
from django.utils import timezone


class Loan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Активен"
        RETURNED = "RETURNED", "Закрыт"

    # связи
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="loans",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
    )

    # даты
    loan_date = models.DateTimeField(default=timezone.now)        # aware
    due_date = models.DateField(null=True, blank=True)            # дата возврата (ожидаемая)
    return_date = models.DateTimeField(null=True, blank=True)     # фактический возврат (aware)

    # служебные
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-loan_date",)
        indexes = [
            models.Index(fields=("user", "book")),
            models.Index(fields=("status",)),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.book} ({self.status})"

    def save(self, *args, **kwargs):

        if self.loan_date is None:
            self.loan_date = timezone.now()

        if self.return_date and self.status != self.Status.RETURNED:
            self.status = self.Status.RETURNED

        if self.due_date and self.due_date < self.loan_date.date():
            self.due_date = self.loan_date.date()

        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.return_date is None

    @property
    def is_overdue(self) -> bool:
        return self.is_active and self.due_date and self.due_date < timezone.localdate()
