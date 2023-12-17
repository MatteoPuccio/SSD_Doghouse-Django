from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from dogs.models import Dog, FavouriteDog
from dogs.serializers import DogSerializer, FavouriteDogSerializer
from dogs.permissions import IsDoghouseWorker
from rest_framework.permissions import IsAuthenticated


class DogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDoghouseWorker]
    queryset = Dog.objects.all()
    serializer_class = DogSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        breed = self.request.query_params.get("breed", None)
        estimated_adult_size = self.request.query_params.get("estimated_adult_size", None)
        birth_date_lte = self.request.query_params.get("birth_date_lte", None)
        birth_date_gte = self.request.query_params.get("birth_date_gte", None)

        if breed is not None:
            qs = qs.filter(breed=breed)
        if estimated_adult_size is not None:
            qs = qs.filter(estimated_adult_size=estimated_adult_size)
        if birth_date_lte is not None:
            qs = qs.filter(birth_date__year__lte=birth_date_lte)
        if birth_date_gte is not None:
            qs = qs.filter(birth_date__year__gte=birth_date_gte)

        return qs.all()


class FavouriteDogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FavouriteDogSerializer
    lookup_field = 'dog_id'

    def get_queryset(self):
        return FavouriteDog.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        favourite_dog = FavouriteDog(user=request.user)
        serializer = self.serializer_class(favourite_dog, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)