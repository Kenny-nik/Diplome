from datetime import timedelta, datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
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
from .models import Book, Loan


# ---------- ГЛАВНАЯ: рекомендации ----------
class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Топ-5 по рейтингу, среди доступных. При равном рейтинге — новее выше.
        context["recommended_books"] = (
            Book.objects.filter(is_available=True)
            .order_by("-rating", "-created_at")[:5]
        )
        return context


# ---------- КАТАЛОГ: фильтрация по жанру, названию и автору ----------
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


# ---------- СОЗДАНИЕ/РЕДАКТИРОВАНИЕ/УДАЛЕНИЕ КНИГ ----------
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
    success_url = reverse_lazy("book_list")

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
        return reverse_lazy("book_detail", kwargs={"pk": self.object.pk})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("book_list")

    def test_func(self):
        return getattr(self.request.user, "is_librarian", False)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Книга успешно удалена!")
        return super().delete(request, *args, **kwargs)


# ---------- ДОБАВИТЬ В «МОИ КНИГИ» ----------
class BookBorrowView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Читатель берёт книгу (Loan). return_date остаётся пустой до возврата.
    """
    def test_func(self):
        return not getattr(self.request.user, "is_librarian", False)

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        if book.available_copies <= 0:
            messages.error(request, "Извините, все экземпляры книги уже выданы.")
            return redirect("book_detail", pk=pk)

        # Уже есть активный займ этой книги?
        existing = Loan.objects.filter(book=book, borrower=request.user, return_date__isnull=True).first()
        if existing:
            messages.warning(request, "Эта книга уже есть в ваших «Моих книгах».")
            return redirect("my_loans")

        Loan.objects.create(book=book, borrower=request.user)
        book.available_copies = max(0, book.available_copies - 1)
        book.is_available = book.available_copies > 0
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(request, f'Книга «{book.title}» добавлена в «Мои книги».')
        return redirect("my_loans")


# ---------- УБРАТЬ ИЗ «МОИХ КНИГ» (возврат) ----------
class BookReturnView(LoginRequiredMixin, View):
    """
    Закрывает активный Loan текущего пользователя по указанной книге.
    """
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        loan = Loan.objects.filter(book=book, borrower=request.user, return_date__isnull=True).first()
        if not loan:
            messages.info(request, "Активной выдачи этой книги у вас нет.")
            return redirect("my_loans")

        loan.return_date = timezone.now().date()
        loan.save(update_fields=["return_date"])

        book.available_copies += 1
        book.is_available = True
        book.save(update_fields=["available_copies", "is_available"])

        messages.success(request, f'Книга «{book.title}» удалена из «Моих книг».')
        return redirect("my_loans")


# ---------- МОИ КНИГИ (веб-страница) ----------
class MyBooksView(LoginRequiredMixin, TemplateView):
    """
    Шаблон получает список активных займов пользователя.
    """
    template_name = "books/my_books.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["loans"] = (
            Loan.objects.filter(borrower=self.request.user, return_date__isnull=True)
            .select_related("book")
            .order_by("-loan_date")
        )
        return ctx
