from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Book
from .serializers import BookSerializer, BookCreateSerializer

class IsLibrarianOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        u = request.user
        return u.is_authenticated and (getattr(u, "is_librarian", False) or u.is_staff)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('title')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre', 'is_available', 'is_premium']
    search_fields = ['title', 'author', 'isbn', 'description']
    ordering_fields = ['title', 'publication_year', 'created_at', 'rating']
    permission_classes = [IsLibrarianOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BookCreateSerializer
        return BookSerializer
