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

    ABSENT_ID_MESSAGE = "Dog id not present in request body"
    ID_NOT_INT_MESSAGE = "Dog id not an integer"
    DOG_NOT_FOUND_MESSAGE = "Dog id not belonging to any registered dog"
    ID_VALIDATED_MESSAGE = "Dog id validated"
    DOG_ADDED_TO_FAVOURITE_MESSAGE = "Dog added to favourites"
    DOG_REMOVED_FROM_FAVOURITE_MESSAGE = "Dog removed from favourites"
    DOG_NOT_IN_FAVOURITES_MESSAGE = "Dog id not belonging to any of the user's favourite dogs"
    DOG_ALREADY_IN_FAVOURITES_MESSAGE = "Dog id already belonging to one of user's favourite dogs"

    @staticmethod
    def __validate_id(request):
        if 'id' not in request.data:
            return FavouriteDogsView.ABSENT_ID_MESSAGE
        if not isinstance(request.data['id'], int):
            return FavouriteDogsView.ID_NOT_INT_MESSAGE
        return FavouriteDogsView.ID_VALIDATED_MESSAGE

    @staticmethod
    def __get_dog_from_id(dog_id):
        dog = Dog.objects.filter(id=dog_id)
        if not dog.exists():
            return None
        return dog.get()

    def post(self, request):
        validation_res = FavouriteDogsView.__validate_id(request)
        if validation_res != FavouriteDogsView.ID_VALIDATED_MESSAGE:
            return Response({'message': validation_res}, status=status.HTTP_400_BAD_REQUEST)

        dog = FavouriteDogsView.__get_dog_from_id(request.data['id'])

        if dog is None:
            return Response({'message': FavouriteDogsView.DOG_NOT_FOUND_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)
        if dog.interested_users.filter(id=request.user.id).exists():
            return Response(data={'message': FavouriteDogsView.DOG_ALREADY_IN_FAVOURITES_MESSAGE},
                            status=status.HTTP_400_BAD_REQUEST)

        dog.interested_users.add(request.user)
        dog.save()

        return Response(data={'message': FavouriteDogsView.DOG_ADDED_TO_FAVOURITE_MESSAGE}, status=status.HTTP_200_OK)

    def get(self, request):
        dogs = list(Dog.objects.filter(interested_users=request.user))
        serializer = DogSerializer(dogs, many=True)
        return Response(data={'favourite-dogs': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request):
        validation_res = FavouriteDogsView.__validate_id(request)
        if validation_res != FavouriteDogsView.ID_VALIDATED_MESSAGE:
            return Response({'message': validation_res}, status=status.HTTP_400_BAD_REQUEST)

        dog = FavouriteDogsView.__get_dog_from_id(request.data['id'])

        if dog is None:
            return Response({'message': FavouriteDogsView.DOG_NOT_FOUND_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        if not dog.interested_users.filter(id=request.user.id).exists():
            return Response(data={'message': FavouriteDogsView.DOG_NOT_IN_FAVOURITES_MESSAGE},
                            status=status.HTTP_400_BAD_REQUEST)

        dog.interested_users.remove(request.user)
        dog.save()

        return Response(data={'message': FavouriteDogsView.DOG_REMOVED_FROM_FAVOURITE_MESSAGE},
                        status=status.HTTP_200_OK)
