from django.shortcuts import render
from rest_framework import viewsets, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dogs.models import Dog
from dogs.serializers import DogSerializer
from dogs.permissions import IsDoghouseWorker


class DogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDoghouseWorker]
    queryset = Dog.objects.all()
    serializer_class = DogSerializer


class FavouriteDogsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if 'id' not in request.data:
            return Response(data={'message': 'Dog id not present in request body'}, status=status.HTTP_400_BAD_REQUEST)
        dog = Dog.objects.filter(id=request.data['id'])
        if not dog.exists():
            return Response(data={'message': 'Dog id not belonging to any registered dog'},
                            status=status.HTTP_400_BAD_REQUEST)
        dog.get().interested_users.add(request.user)
        dog.get().save()
        return Response(data={'message': 'Dog added to favourites'}, status=status.HTTP_200_OK)
