from django.urls import path, include
from . import views

urlpatterns = [
    # Web interface URLs
    path('', views.BookListView.as_view(), name='book_list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('create/', views.BookCreateView.as_view(), name='book_create'),
    path('<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    path('<int:pk>/borrow/', views.BookBorrowView.as_view(), name='book_borrow'),
    path('my-books/', views.MyBooksView.as_view(), name='my_loans'),

    # API URLs (оставляем существующие)
    path('api/', include('apps.books.api_urls')),
    path('my-books/', views.MyBooksView.as_view(), name='my_books'),
]