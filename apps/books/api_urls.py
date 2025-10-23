from rest_framework.routers import DefaultRouter
from .api import BookViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='book')

urlpatterns = router.urls