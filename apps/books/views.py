from datetime import timedelta
from itertools import chain

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Book
from apps.loans.models import Loan


# ---- утилита: активна ли подписка у пользователя
def _has_active_subscription(user) -> bool:
    try:
        sub = user.profile.subscription_until
        return bool(sub and sub >= timezone.now().date())
    except Exception:
        return False


# ---------- ГЛАВНАЯ: рекомендации ----------
class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Премиум книги показываем приоритетно, но суммарно не более 5
        premium = Book.objects.filter(is_available=True, is_premium=True).order_by("-rating", "-created_at")[:5]
        usual = Book.objects.filter(is_available=True, is_premium=False).order_by("-rating", "-created_at")[:5]
        combined = list(chain(premium, usual))[:5]

        ctx["recommended_books"] = combined
        return ctx


# ---------- КАТАЛОГ ----------
class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 24

    GENRE_ALIASES = {
        "sci_fi": {"sci_fi", "sci-fi", "science_fiction", "научная фантастика"},
        "romance": {"romance", "роман"},
        "history": {"history", "история"},
        "cs": {"cs", "programming", "программирование", "python", "айти"},
        "science": {"science", "наука"},
        "detective": {"detective", "детектив", "mystery"},
        "poetry": {"poetry", "поэзия"},
        "other": {"other", "другое", ""},
    }

    def _canonize_genre(self, raw: str) -> str:
        g = (raw or "").strip().lower()
        if not g:
            return ""
        for code, variants in self.GENRE_ALIASES.items():
            if g in variants:
                return code
        for code, name in getattr(Book, "GENRE_CHOICES", []):
            if g == (name or "").lower():
                return code
        return g

    def get_queryset(self):
        qs = Book.objects.all()

        q = (self.request.GET.get("q") or self.request.GET.get("search") or "").strip()
        author = (self.request.GET.get("author") or "").strip()
        genre_raw = (self.request.GET.get("genre") or "").strip()
        genre_code = self._canonize_genre(genre_raw)

        if q:
            qs = qs.filter(title__icontains=q)
        if author:
            qs = qs.filter(author__icontains=author)
        if genre_code:
            qs = qs.filter(Q(genre__iexact=genre_code) | Q(genre__iexact=genre_raw))

        # Сортируем стабильнее: по названию
        return qs.order_by("title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = getattr(Book, "GENRE_CHOICES", [])
        ctx["current"] = {
            "q": self.request.GET.get("q", self.request.GET.get("search", "")),
            "author": self.request.GET.get("author", ""),
            "genre": self.request.GET.get("genre", ""),
        }
        # чтобы в шаблоне можно было отключать кнопки для премиум без подписки
        user = self.request.user
        ctx["has_premium"] = user.is_authenticated and _has_active_subscription(user)
        return ctx


# ---------- ДЕТАЛИ КНИГИ ----------
class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book = self.object
        user = self.request.user

        can_borrow = (
            user.is_authenticated
            and not getattr(user, "is_librarian", False)
            and book.is_available
            and (book.available_copies or 0) > 0
        )

        # Запрет на премиум без подписки
        if can_borrow and book.is_premium and not _has_active_subscription(user):
            can_borrow = False

        ctx["can_borrow"] = can_borrow
        ctx["requires_premium"] = bool(book.is_premium)
        ctx["has_premium"] = user.is_authenticated and _has_active_subscription(user)
        return ctx


# ---------- CRUD для библиотекаря ----------
class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    template_name = "books/book_form.html"
    fields = [
        "title", "author", "isbn", "publication_year", "genre", "description",
        "cover_url", "rating", "total_copies", "available_copies",
        "is_available", "is_premium",
    ]
    success_url = reverse_lazy("books:book_list")

    def test_func(self):
        u = self.request.user
        return getattr(u, "is_librarian", False) or u.is_staff

    def form_valid(self, form):
        messages.success(self.request, "Книга успешно добавлена!")
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = "books/book_form.html"
    fields = [
        "title", "author", "isbn", "publication_year", "genre", "description",
        "cover_url", "rating", "total_copies", "available_copies",
        "is_available", "is_premium",
    ]

    def test_func(self):
        u = self.request.user
        return getattr(u, "is_librarian", False) or u.is_staff

    def form_valid(self, form):
        messages.success(self.request, "Книга успешно обновлена!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("books:book_detail", kwargs={"pk": self.object.pk})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:book_list")

    def test_func(self):
        u = self.request.user
        return getattr(u, "is_librarian", False) or u.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Книга успешно удалена!")
        return super().delete(request, *args, **kwargs)


# ---------- Добавить в «Мои книги» ----------
class BookBorrowView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        # Жёсткий запрет: премиум без подписки
        if book.is_premium and not _has_active_subscription(request.user):
            messages.error(request, "Эта книга доступна только по подписке. "
                                    "Оформите подписку, чтобы получить доступ.")
            return redirect("users:subscribe")

        if (book.available_copies or 0) <= 0:
            messages.error(request, "Извините, все экземпляры уже выданы.")
            return redirect("books:book_detail", pk=pk)

        if Loan.objects.filter(user=request.user, book=book, return_date__isnull=True).exists():
            messages.warning(request, "Вы уже взяли эту книгу.")
            return redirect("books:book_detail", pk=pk)

        loan = Loan.objects.create(
            book=book,
            user=request.user,
            due_date=timezone.now().date() + timedelta(days=14),
        )

        book.available_copies = max(0, (book.available_copies or 0) - 1)
        book.is_available = book.available_copies > 0
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(
            request,
            f'Книга «{book.title}» добавлена. Верните до {loan.due_date.strftime("%d.%m.%Y")}.'
        )
        return redirect("books:book_detail", pk=pk)


# ---------- Вернуть / убрать из «моих книг» ----------
class BookReturnView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        loan = Loan.objects.filter(book=book, user=request.user, return_date__isnull=True).first()
        if not loan:
            messages.info(request, "Активной выдачи этой книги у вас нет.")
            return redirect("books:my_books")

        loan.return_date = timezone.now()
        loan.save(update_fields=["return_date", "status"])

        book.available_copies = (book.available_copies or 0) + 1
        book.is_available = True
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(request, f'Книга «{book.title}» удалена из «Моих книг».')
        return redirect("books:my_books")


# ---------- Снять книгу из "моих книг" ----------
class BookRemoveView(LoginRequiredMixin, View):
    """Убирает активную выдачу и возвращает назад на 'Мои книги'."""
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        loan = Loan.objects.filter(
            user=request.user, book=book, return_date__isnull=True
        ).first()

        if not loan:
            messages.info(request, "У вас нет активной выдачи этой книги.")
            return redirect("books:my_books")

        # закрываем выдачу
        loan.return_date = timezone.now()
        loan.save(update_fields=["return_date", "status"])

        # возвращаем экземпляр в доступные
        book.available_copies = (book.available_copies or 0) + 1
        book.is_available = True
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(request, f'Книга «{book.title}» убрана из «Моих книг».')
        return redirect("books:my_books")


# ---------- Мои книги ----------
class MyBooksView(LoginRequiredMixin, TemplateView):
    template_name = "books/my_books.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["loans"] = (
            Loan.objects.filter(user=self.request.user, return_date__isnull=True)
            .select_related("book")
            .order_by("-loan_date")
        )
        # вдруг пригодится в шаблоне
        ctx["has_premium"] = _has_active_subscription(self.request.user)
        return ctx


class BooksCatalogView(BookListView):
    """Обёртка для совместимости с web_urls.py."""
    pass
