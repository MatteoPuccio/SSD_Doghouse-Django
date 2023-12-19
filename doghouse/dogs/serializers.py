from rest_framework import serializers, validators

from dogs.models import Dog, FavouriteDog


class DogSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data['entry_date'] < data['birth_date']:
            raise serializers.ValidationError("Entry date must be after birth date")
        return data

    class Meta:
        fields = ('id', 'name', 'breed', 'sex', 'birth_date', 'entry_date', 'neutered',
                  'description', 'estimated_adult_size', 'picture')
        model = Dog


class FavouriteDogSerializer(serializers.ModelSerializer):
    dog_id = serializers.PrimaryKeyRelatedField(queryset=Dog.objects.all(), source='dog', write_only=True)
    dog = DogSerializer(read_only=True)

    class Meta:
        fields = ('user', 'dog', 'dog_id')
        read_only_fields = ['user']
        model = FavouriteDog
        validators = [
            validators.UniqueTogetherValidator(
                queryset=FavouriteDog.objects.all(),
                fields=['user', 'dog_id']
            )
        ]
