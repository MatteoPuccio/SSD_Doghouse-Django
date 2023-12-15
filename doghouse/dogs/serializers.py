from rest_framework import serializers

from dogs.models import Dog


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'breed', 'sex', 'birth_date', 'entry_date', 'neutered',
                  'description', 'estimated_adult_size', 'picture')
        model = Dog

