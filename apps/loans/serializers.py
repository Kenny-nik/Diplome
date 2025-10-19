from rest_framework import serializers
from .models import Loan
from apps.books.serializers import BookSerializer
from apps.users.serializers import UserCreateSerializer


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id', 'book', 'book_title', 'book_author',
            'user', 'user_email', 'user_name',
            'loan_date', 'due_date', 'return_date', 'status',
            'is_overdue', 'days_overdue', 'created_at'
        ]
        read_only_fields = ['id', 'loan_date', 'status', 'created_at']


class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['book', 'user', 'due_date']

    def validate(self, data):
        book = data['book']
        user = data['user']

        # Проверка доступности книги
        if not book.is_available:
            raise serializers.ValidationError("Книга недоступна для выдачи")

        # Проверка, не превышает ли пользователь лимит займов
        active_loans = Loan.objects.filter(user=user, status='ACTIVE').count()
        if active_loans >= 5:
            raise serializers.ValidationError("Превышен лимит активных займов (максимум 5)")

        return data

    def create(self, validated_data):
        loan = Loan.objects.create(**validated_data)

        book = loan.book
        book.available_copies -= 1
        if book.available_copies == 0:
            book.is_available = False
        book.save()

        return loan


class LoanReturnSerializer(serializers.Serializer):
    return_date = serializers.DateTimeField(required=False)

    def update(self, instance, validated_data):
        instance.mark_returned()
        return instance