from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Loan
from .forms import BookForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from .models import Book, Loan

from .models import Book, Loan
from .serializers import (
    BookSerializer, BookCreateSerializer,
    LoanSerializer, LoanCreateSerializer
)
from .permissions import IsLibrarian, IsOwnerOrLibrarian


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre', 'author', 'is_available']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'author', 'publication_year', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return BookCreateSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsLibrarian]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def borrow(self, request, pk=None):
        book = self.get_object()
        if book.available_copies <= 0:
            return Response(
                {'error': 'No copies available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan = Loan.objects.create(
            book=book,
            user=request.user,
            due_date=request.data.get('due_date')
        )
        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrLibrarian]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_returned', 'user', 'book']
    ordering_fields = ['loan_date', 'due_date', 'return_date']

    def get_queryset(self):
        if self.request.user.role == 'LIBRARIAN':
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return LoanCreateSerializer
        return LoanSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsLibrarian])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        loan.return_book()
        serializer = self.get_serializer(loan)
        return Response(serializer.data)

class BookListView(LoginRequiredMixin, View):
    def get(self, request):
        books = Book.objects.all()
        return render(request, 'books/book_list.html', {'books': books})

class BookCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_librarian:
            return redirect('book_list')
        form = BookForm()
        return render(request, 'books/book_form.html', {'form': form})

    def post(self, request):
        if not request.user.is_librarian:
            return redirect('book_list')
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
        return render(request, 'books/book_form.html', {'form': form})

class BookUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.is_librarian:
            return redirect('book_list')
        book = get_object_or_404(Book, pk=pk)
        form = BookForm(instance=book)
        return render(request, 'books/book_form.html', {'form': form})

    def post(self, request, pk):
        if not request.user.is_librarian:
            return redirect('book_list')
        book = get_object_or_404(Book, pk=pk)
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
        return render(request, 'books/book_form.html', {'form': form})

class BookDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_librarian:
            return redirect('book_list')
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return redirect('book_list')


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.all()

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )

        # Filters
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)

        author = self.request.GET.get('author')
        if author:
            queryset = queryset.filter(author__icontains=author)

        available = self.request.GET.get('available')
        if available == 'true':
            queryset = queryset.filter(is_available=True)
        elif available == 'false':
            queryset = queryset.filter(is_available=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Book.BOOK_GENRES
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['title', 'author', 'isbn', 'publication_year', 'genre', 'description', 'total_copies']
    success_url = reverse_lazy('book_list')

    def test_func(self):
        return self.request.user.is_librarian

    def form_valid(self, form):
        messages.success(self.request, 'Книга успешно добавлена!')
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['title', 'author', 'isbn', 'publication_year', 'genre', 'description', 'total_copies']

    def test_func(self):
        return self.request.user.is_librarian

    def form_valid(self, form):
        messages.success(self.request, 'Книга успешно обновлена!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def test_func(self):
        return self.request.user.is_librarian

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Книга успешно удалена!')
        return super().delete(request, *args, **kwargs)


class BookBorrowView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.is_librarian  # Only readers can borrow

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        if book.available_copies <= 0:
            messages.error(request, 'Извините, все экземпляры книги уже выданы')
            return redirect('book_detail', pk=pk)

        # Check if user already has this book
        existing_loan = Loan.objects.filter(book=book, user=request.user, is_returned=False).first()
        if existing_loan:
            messages.warning(request, 'Вы уже взяли эту книгу')
            return redirect('book_detail', pk=pk)

        # Create loan
        from datetime import datetime, timedelta
        loan = Loan.objects.create(
            book=book,
            user=request.user,
            due_date=datetime.now() + timedelta(days=14)  # 2 weeks
        )

        # Update book availability
        book.available_copies -= 1
        if book.available_copies == 0:
            book.is_available = False
        book.save()

        messages.success(request,
                         f'Книга "{book.title}" успешно взята! Верните до {loan.due_date.strftime("%d.%m.%Y")}')
        return redirect('my_loans')