from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.utils import timezone

from .models import Book
from apps.loans.models import Loan


# ---------- ГЛАВНАЯ: рекомендации ----------
class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recommended_books"] = (
            Book.objects.filter(is_available=True)
            .order_by("-rating", "-created_at")[:5]
        )
        return context


# ---------- КАТАЛОГ ----------
class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 24

    def get_queryset(self):
        qs = Book.objects.all()

        q = (self.request.GET.get("q") or self.request.GET.get("search") or "").strip()
        author = (self.request.GET.get("author") or "").strip()
        genre = (self.request.GET.get("genre") or "").strip()

        if q:
            qs = qs.filter(title__icontains=q)
        if author:
            qs = qs.filter(author__icontains=author)
        if genre:
            qs = qs.filter(genre=genre)

        return qs.order_by("title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Book.BOOK_GENRES
        ctx["current"] = {
            "q": self.request.GET.get("q", self.request.GET.get("search", "")),
            "author": self.request.GET.get("author", ""),
            "genre": self.request.GET.get("genre", ""),
        }
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
        ctx["can_borrow"] = (
            user.is_authenticated
            and not getattr(user, "is_librarian", False)
            and book.is_available
            and (book.available_copies or 0) > 0
        )
        return ctx


# ---------- CRUD для библиотекаря ----------
class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    template_name = "books/book_form.html"
    fields = [
        "title",
        "author",
        "isbn",
        "publication_year",
        "genre",
        "description",
        "cover_url",
        "rating",
        "total_copies",
        "available_copies",
        "is_available",
    ]
    success_url = reverse_lazy("books:book_list")

    def test_func(self):
        return getattr(self.request.user, "is_librarian", False)

    def form_valid(self, form):
        messages.success(self.request, "Книга успешно добавлена!")
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = "books/book_form.html"
    fields = [
        "title",
        "author",
        "isbn",
        "publication_year",
        "genre",
        "description",
        "cover_url",
        "rating",
        "total_copies",
        "available_copies",
        "is_available",
    ]

    def test_func(self):
        return getattr(self.request.user, "is_librarian", False)

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
        return getattr(self.request.user, "is_librarian", False)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Книга успешно удалена!")
        return super().delete(request, *args, **kwargs)


# ---------- Добавить в «Мои книги» ----------
class BookBorrowView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        if (book.available_copies or 0) <= 0:
            messages.error(request, "Извините, все экземпляры уже выданы.")
            return redirect("books:book_detail", pk=pk)

        # запрет на повторную выдачу той же книги
        if Loan.objects.filter(user=request.user, book=book, return_date__isnull=True).exists():
            messages.warning(request, "Вы уже взяли эту книгу.")
            return redirect("books:book_detail", pk=pk)

        loan = Loan.objects.create(
            book=book,
            user=request.user,
            # Берём «сегодня» независимо от USE_TZ
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

        loan.return_date = timezone.now()   # DateTimeField
        loan.save(update_fields=["return_date", "status"])

        book.available_copies = (book.available_copies or 0) + 1
        book.is_available = True
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(request, f'Книга «{book.title}» удалена из «Моих книг».')
        return redirect("books:my_books")


class BookRemoveView(LoginRequiredMixin, View):
    """Снять книгу из 'моих книг' (символическое 'вернуть')."""
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        loan = Loan.objects.filter(user=request.user, book=book, return_date__isnull=True).first()
        if not loan:
            messages.info(request, "У вас нет активной выдачи этой книги.")
            return redirect("books:book_detail", pk=pk)

        loan.return_date = timezone.now()   # DateTimeField
        loan.save(update_fields=["return_date", "status"])

        book.available_copies = (book.available_copies or 0) + 1
        book.is_available = True
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(request, f'Книга «{book.title}» убрана из "Моих книг".')
        return redirect("books:book_detail", pk=pk)


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
        return ctx


class BooksCatalogView(BookListView):
    """Обёртка для совместимости с web_urls.py."""
    pass
