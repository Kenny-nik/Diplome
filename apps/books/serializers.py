from rest_framework import serializers
from .models import Book
from apps.loans.models import Loan
from apps.users.models import User


class BookSerializer(serializers.ModelSerializer):
    available_copies = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'publication_year',
            'genre', 'description', 'total_copies', 'available_copies',
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'publication_year',
            'genre', 'description', 'total_copies'
        ]


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id', 'book', 'book_title', 'user', 'user_email',
            'loan_date', 'due_date', 'return_date', 'is_returned'
        ]
        read_only_fields = ['id', 'loan_date', 'return_date', 'is_returned']


class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['book', 'user', 'due_date']

    def validate(self, data):
        book = data['book']
        if book.available_copies <= 0:
            raise serializers.ValidationError("No copies available for loan")
        return data