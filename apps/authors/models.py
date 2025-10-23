from django.db import models

class Author(models.Model):
    name = models.CharField("Имя автора", max_length=255, unique=True)
    country = models.CharField("Страна", max_length=128, blank=True)
    birth_year = models.IntegerField("Год рождения", null=True, blank=True)
    death_year = models.IntegerField("Год смерти", null=True, blank=True)
    about = models.TextField("О авторе", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return self.name
