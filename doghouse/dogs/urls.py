from django.urls import path

from dogs.views import DogViewSet, FavouriteDogViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('favourite-dogs', FavouriteDogViewSet, basename='favourite-dogs')
router.register('', DogViewSet, basename='dogs')

urlpatterns = router.urls
