from django.urls import path, include
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
    BookBorrowView,
    BookReturnView,
    MyBooksView,
)

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("create/", BookCreateView.as_view(), name="book_create"),
    path("<int:pk>/update/", BookUpdateView.as_view(), name="book_update"),
    path("<int:pk>/delete/", BookDeleteView.as_view(), name="book_delete"),
    path("<int:pk>/borrow/", BookBorrowView.as_view(), name="book_borrow"),
    path("<int:pk>/remove/", BookReturnView.as_view(), name="book_remove"),
    path("my-books/", MyBooksView.as_view(), name="my_loans"),

    path("api/", include("apps.books.api_urls")),
]
