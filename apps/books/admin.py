from django.contrib import admin
from django.utils.html import format_html
from .models import Book
from apps.loans.models import Loan


class ActiveLoanInline(admin.TabularInline):
    """Показываем активные выдачи по книге прямо в карточке книги."""
    model = Loan
    extra = 0
    fields = ("user", "loan_date", "due_date", "return_date", "status")
    readonly_fields = ("user", "loan_date", "due_date", "return_date", "status")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(return_date__isnull=True)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title", "author", "genre", "rating",
        "total_copies", "available_copies", "is_available", "cover_preview",
    )
    list_filter = ("genre", "is_available")
    search_fields = ("title", "author", "isbn")
    readonly_fields = ("created_at", "updated_at", "slug", "cover_preview_large")
    inlines = (ActiveLoanInline,)
    fieldsets = (
        ("Основное", {
            "fields": ("title", "slug", "author", "isbn", "publication_year", "genre", "description")
        }),
        ("Обложка", {
            "fields": ("cover_image", "cover_url", "cover_preview_large"),
        }),
        ("Статистика", {
            "fields": ("rating", "total_copies", "available_copies", "is_available", "created_at", "updated_at"),
        }),
    )

    def cover_preview(self, obj):
        url = obj.preferred_cover
        if url:
            return format_html('<img src="{}" style="height:48px;border-radius:4px;" />', url)
        return "—"
    cover_preview.short_description = "Обложка"

    def cover_preview_large(self, obj):
        url = obj.preferred_cover
        if url:
            return format_html('<img src="{}" style="height:160px;border-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,.1);" />', url)
        return "—"
    cover_preview_large.short_description = "Превью"


from django.contrib import admin as _site
_site.site_header = "Библиотека — администрирование"
_site.site_title = "Библиотека — админ"
_site.index_title = "Управление сайтом"