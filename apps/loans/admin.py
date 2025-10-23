from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "loan_date", "due_date", "return_date", "status")
    list_filter = ("status", "loan_date", "due_date")
    search_fields = ("book__title", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-loan_date",)