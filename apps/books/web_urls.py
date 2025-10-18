from django.urls import path
from . import views as v

urlpatterns = [
    # каталог
    path("", v.BooksCatalogView.as_view(), name="book_list"),

    # CRUD (для библиотекаря)
    path("create/", v.BookCreateView.as_view(), name="book_create"),
    path("<int:pk>/edit/", v.BookUpdateView.as_view(), name="book_update"),
    path("<int:pk>/delete/", v.BookDeleteView.as_view(), name="book_delete"),

    # детали + действия читателя
    path("<int:pk>/", v.BookDetailView.as_view(), name="book_detail"),
    path("<int:pk>/borrow/", v.BookBorrowView.as_view(), name="book_borrow"),
    path("<int:pk>/remove/", v.BookReturnView.as_view(), name="book_remove"),

    # мои книги (активные займы)
    path("my-books/", v.MyBooksView.as_view(), name="my_books"),
]
