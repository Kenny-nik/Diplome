from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static
from apps.books.views import HomePageView, BookListView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Auth (если используешь стандартные шаблоны)
    path("login/", include("django.contrib.auth.urls")),

    # Web-приложения
    path("books/", include("apps.books.urls")),
    path("loans/", include("apps.loans.urls")),
    path("users/", include("apps.users.urls")),

    # API
    path("api/v1/", include([
        path("books/", include("apps.books.api_urls")),
        path("loans/", include("apps.loans.api_urls")),
    ])),

    # Документация API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Главная и каталог
    path("", HomePageView.as_view(), name="home"),
    path("catalog/", BookListView.as_view(), name="book_list"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)