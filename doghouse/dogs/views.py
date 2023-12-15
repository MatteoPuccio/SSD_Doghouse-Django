from django.shortcuts import render
from rest_framework import viewsets

from dogs.models import Dog
from dogs.serializers import DogSerializer
from dogs.permissions import IsDoghouseWorker


class DogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDoghouseWorker]
    queryset = Dog.objects.all()
    serializer_class = DogSerializer
