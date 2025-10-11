from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Loan
from .serializers import LoanSerializer, LoanCreateSerializer, LoanReturnSerializer
from .permissions import IsLibrarian, IsOwnerOrLibrarian


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'user', 'book']
    ordering_fields = ['loan_date', 'due_date', 'return_date']

    def get_queryset(self):
        user = self.request.user

        if user.is_librarian:
            return Loan.objects.all().select_related('book', 'user')
        else:
            return Loan.objects.filter(user=user).select_related('book', 'user')

    def get_serializer_class(self):
        if self.action == 'create':
            return LoanCreateSerializer
        elif self.action == 'return_book':
            return LoanReturnSerializer
        return LoanSerializer

    def get_permissions(self):
        if self.action in ['create', 'return_book']:
            permission_classes = [IsAuthenticated, IsLibrarian]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrLibrarian]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Возврат книги"""
        loan = self.get_object()
        serializer = self.get_serializer(loan, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': f'Книга "{loan.book.title}" успешно возвращена'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        """Мои займы (для обычных пользователей)"""
        if request.user.is_librarian:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Просроченные займы"""
        from django.utils import timezone
        queryset = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status='ACTIVE'
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)