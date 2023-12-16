from django.urls import path

from dogs.views import DogViewSet, FavouriteDogsView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', DogViewSet, basename='dogs')

urlpatterns = [] + router.urls
