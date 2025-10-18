from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.books.views import HomePageView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Auth (стандартные шаблоны Django)
    path("login/", include("django.contrib.auth.urls")),

    # Web-приложения
    path(
        "books/",
        include(("apps.books.web_urls", "books"), namespace="books"),
    ),
    path("loans/", include("apps.loans.urls")),
    path("users/", include("apps.users.urls")),

    # API
    path("api/v1/books/", include("apps.books.api_urls")),
    path("api/v1/loans/", include("apps.loans.api_urls")),

    # Документация API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Главная
    path("", HomePageView.as_view(), name="home"),

    # Удобный алиас на каталог — редирект на books:book_list
    path("catalog/", RedirectView.as_view(pattern_name="books:book_list", permanent=False), name="catalog"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
