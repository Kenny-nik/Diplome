from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country", "birth_year", "death_year", "created_at")
    search_fields = ("name", "country")
    list_filter = ("country",)
