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


class DashboardView(TemplateView):
    template_name = "librarian/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        User = get_user_model()
        today = timezone.now().date()

        ctx["users_count"] = User.objects.count()
        ctx["active_users"] = User.objects.filter(is_active=True).count()

        loans_qs = Loan.objects.select_related("book", "user")
        ctx["loans_count"] = loans_qs.count()

        active_qs = loans_qs.filter(return_date__isnull=True)
        ctx["active_loans"] = active_qs.count()
        ctx["overdue_loans"] = active_qs.filter(due_date__lt=today).count()

        ctx["last_loans"] = loans_qs.order_by("-loan_date")[:20]
        return ctx


class UsersListView(ListView):
    template_name = "librarian/users.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        User = get_user_model()
        qs = User.objects.all().order_by("email")

        q = (self.request.GET.get("q") or "").strip()
        active = (self.request.GET.get("active") or "").strip()  # yes|no|""
        staff = (self.request.GET.get("staff") or "").strip()    # yes|no|""

        if q:
            qs = qs.filter(
                Q(email__icontains=q)
                | Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        if active in ("yes", "no"):
            qs = qs.filter(is_active=(active == "yes"))
        if staff in ("yes", "no"):
            qs = qs.filter(is_staff=(staff == "yes"))
        return qs


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
