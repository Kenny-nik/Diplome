from rest_framework.routers import DefaultRouter
from .api import AuthorViewSet

router = DefaultRouter()
router.register(r"", AuthorViewSet, basename="author")
urlpatterns = router.urls
