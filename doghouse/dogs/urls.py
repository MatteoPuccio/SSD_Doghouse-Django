from dogs.views import DogViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', DogViewSet, basename='dogs')

urlpatterns = router.urls
