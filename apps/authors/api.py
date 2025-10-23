from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Author
from .serializers import AuthorSerializer

class IsLibrarianOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        u = request.user
        return u.is_authenticated and (getattr(u, "is_librarian", False) or u.is_staff)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by("name")
    serializer_class = AuthorSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "country"]
    filterset_fields = ["country", "birth_year", "death_year"]
    ordering_fields = ["name", "birth_year", "created_at"]
