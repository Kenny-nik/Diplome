from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView, ListView

from apps.loans.models import Loan

User = get_user_model()


class LibrarianAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Доступ только библиотекарям:
    - is_staff = True ИЛИ
    - состоит в группе "Библиотекарь"
    """
    def test_func(self):
        u = self.request.user
        return u.is_staff or u.groups.filter(name="Библиотекарь").exists()


class DashboardView(LibrarianAccessMixin, TemplateView):
    template_name = "librarian/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()

        ctx["total_users"] = User.objects.count()
        ctx["active_users"] = User.objects.filter(is_active=True).count()

        ctx["total_loans"] = Loan.objects.count()
        ctx["active_loans"] = Loan.objects.filter(return_date__isnull=True).count()
        ctx["overdue_loans"] = Loan.objects.filter(
            return_date__isnull=True, due_date__lt=today
        ).count()

        ctx["recent_loans"] = (
            Loan.objects.select_related("book", "user")
            .order_by("-loan_date")[:10]
        )
        return ctx


class UsersListView(LibrarianAccessMixin, ListView):
    model = User
    template_name = "librarian/users.html"
    context_object_name = "users"
    paginate_by = 25
    ordering = "-date_joined"

    def get_queryset(self):
        qs = User.objects.all()
        q = (self.request.GET.get("q") or "").strip()
        is_active = self.request.GET.get("is_active")
        is_staff = self.request.GET.get("is_staff")

        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        if is_active in {"yes", "no"}:
            qs = qs.filter(is_active=(is_active == "yes"))
        if is_staff in {"yes", "no"}:
            qs = qs.filter(is_staff=(is_staff == "yes"))

        return qs.order_by(self.ordering)


class LoansListView(LibrarianAccessMixin, ListView):
    model = Loan
    template_name = "librarian/loans.html"
    context_object_name = "loans"
    paginate_by = 25

    def get_queryset(self):
        qs = Loan.objects.select_related("book", "user")
        q = (self.request.GET.get("q") or "").strip()
        status = self.request.GET.get("status")  # active / overdue / returned

        if q:
            qs = qs.filter(
                Q(book__title__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
            )

        today = timezone.localdate()
        if status == "active":
            qs = qs.filter(return_date__isnull=True)
        elif status == "overdue":
            qs = qs.filter(return_date__isnull=True, due_date__lt=today)
        elif status == "returned":
            qs = qs.filter(return_date__isnull=False)

        return qs.order_by("-loan_date")
