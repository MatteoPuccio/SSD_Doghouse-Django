import datetime

import pytest
from django.core.exceptions import ValidationError
from rest_framework import serializers
from mixer.backend.django import mixer
from dogs.models import picture_source_prefix, Dog
from dogs.serializers import DogSerializer

dog_model = 'dogs.Dog'


@pytest.fixture()
def today_date():
    return datetime.date.today()


@pytest.mark.parametrize('name', ['Pluto', 'Goku', 'Pochita'])
def test_valid_dog_name(db, name):
    dog = mixer.blend(dog_model, name=name)
    assert dog.name == name


def test_dog_not_start_uppercase(db):
    dog = mixer.blend(dog_model, name='pluto')
    with pytest.raises(ValidationError):
        dog.full_clean()


def test_dog_uppercase_in_middle(db):
    dog = mixer.blend(dog_model, name='plUto')
    with pytest.raises(ValidationError):
        dog.full_clean()


def test_name_length_21_chars_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, name='A' * 21, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_name_length_1_chars_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, name='A', entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_name_no_name_equals_unnamed(db):
    dog = mixer.blend(dog_model)
    assert dog.name == 'Unnamed'


@pytest.mark.parametrize('name', ['g4nz0', 'dragonball$', '<alert>'])
def test_name_containing_invalid_chars_raises_exception(db, name, today_date):
    dog = mixer.blend(dog_model, name=name, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('breed', ['American Hairless Terrier', 'Dutch Shepherd Dog',
                                   'Great Dane', 'Spanish Mastiff'])
def test_valid_breed(db, breed):
    dog = mixer.blend(dog_model, breed=breed)
    assert dog.breed == breed


def test_breed_not_in_dogs_breed_json_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, breed='Cheems', entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('sex', ['M', 'F'])
def test_valid_sex(db, sex):
    dog = mixer.blend(dog_model, sex=sex)
    assert dog.sex == sex


def test_sex_not_valid_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, sex='Xrlg', entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('birth_date', [datetime.date(2005, 12, 31),
                                        datetime.date(2008, 1, 24),
                                        datetime.date(2011, 5, 11)])
def test_valid_birth_date(db, birth_date, today_date):
    dog = mixer.blend(dog_model, birth_date=birth_date, entry_date=today_date)
    assert dog.birth_date == birth_date


def test_birth_date_earlier_than_1980_raises_exception(db, today_date):
    date = datetime.date(1979, 1, 24)
    dog = mixer.blend(dog_model, birth_date=date, entry_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_birth_date_older_than_today_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, birth_date=today_date + datetime.timedelta(days=1), entry_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('entry_date', [datetime.date(2005, 12, 31),
                                        datetime.date(2008, 1, 24),
                                        datetime.date(2011, 5, 11)])
def test_valid_entry_date(db, entry_date):
    dog = mixer.blend(dog_model, entry_date=entry_date, birth_date=entry_date - datetime.timedelta(days=1))
    assert dog.entry_date == entry_date


def test_entry_date_earlier_than_1980_raises_exception(db):
    date = datetime.date(1979, 1, 24)
    dog = mixer.blend(dog_model, entry_date=date, birth_date=date - datetime.timedelta(1))
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_entry_date_older_than_today_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, entry_date=today_date + datetime.timedelta(days=1), birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_entry_date_earlier_than_birth_date_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, entry_date=today_date - datetime.timedelta(days=1), birth_date=today_date)
    serializer = DogSerializer(dog)
    serializer = DogSerializer(data=serializer.data)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)


def test_neutered_exists(db):
    dog = mixer.blend(dog_model)
    assert dog.neutered is not None


@pytest.mark.parametrize('description', ['Lorem ipsum dolor sit amet, consectetur adipiscing elit',
                                         'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                                         'Ut enim ad minim veniam, quis nostrud exercitation ullamco',
                                         ''])
def test_valid_description(db, description):
    dog = mixer.blend(dog_model, description=description)
    assert dog.description == description


def test_description_longer_than_400_chars_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, description='A' * 401, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('description', ['dog$', '/1)cn', '(&~', '<alert>'])
def test_description_containing_invalid_chars_raises_exception(db, description, today_date):
    dog = mixer.blend(dog_model, description=description, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_description_containing_special_characters(db):
    description = ';,.!? 1-\t'
    dog = mixer.blend(dog_model, description=description)
    assert dog.description == description


@pytest.mark.parametrize('estimated_adult_size', ['XS', 'S', 'M', 'L', 'XL'])
def test_valid_estimated_adult_size(db, estimated_adult_size):
    dog = mixer.blend(dog_model, estimated_adult_size=estimated_adult_size)
    assert dog.estimated_adult_size == estimated_adult_size


def test_estimated_adult_size_not_in_dict_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, estimated_adult_size='XXXXL', entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('picture', [picture_source_prefix + 'x.png',
                                     picture_source_prefix + 'c.jpeg',
                                     picture_source_prefix + 'test.jpg',
                                     ''])
def test_valid_picture(db, picture):
    dog = mixer.blend(dog_model, picture=picture)
    assert dog.picture == picture


def test_picture_not_from_source_raises_exception(db, today_date):
    dog = mixer.blend(dog_model, picture='https://example.com', entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('picture', [picture_source_prefix + '<script>alert(20)</script>.png',
                                     picture_source_prefix + '_.jpg',
                                     picture_source_prefix + '$/~.jpeg'])
def test_picture_contains_invalid_characters_raises_exception(db, picture, today_date):
    dog = mixer.blend(dog_model, picture=picture, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('picture', [picture_source_prefix + 'x.gif',
                                     picture_source_prefix + 'c.mp4',
                                     picture_source_prefix + 'test'])
def test_picture_not_valid_format_raises_exception(db, picture, today_date):
    dog = mixer.blend(dog_model, picture=picture, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_picture_length_201_raises_exception(db, today_date):
    picture = 'A' * (201 - len(picture_source_prefix))
    dog = mixer.blend(dog_model, picture=picture_source_prefix + picture, entry_date=today_date, birth_date=today_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_valid_dog(db):
    name = 'Pluto'
    breed = 'Spanish Mastiff'
    sex = 'M'
    birth_date = datetime.date(2000, 1, 2)
    entry_date = datetime.date(2000, 1, 3)
    neutered = True
    description = 'Pluto di Topolino'
    estimated_adult_size = 'L'
    picture = 'https://disney.com/pluto.png'

    dog = mixer.blend(dog_model, name=name, breed=breed, sex=sex,
                      birth_date=birth_date,
                      entry_date=entry_date,
                      neutered=neutered,
                      description=description,
                      estimated_adult_size=estimated_adult_size,
                      picture=picture
                      )
    assert dog.name == name and dog.breed == breed and dog.sex == sex \
           and dog.birth_date == birth_date \
           and dog.entry_date == entry_date \
           and dog.neutered == neutered and dog.description == description \
           and dog.estimated_adult_size == estimated_adult_size and dog.picture == picture


def test_dog_to_str(db):
    dog = mixer.blend(dog_model, name='Pluto')
    assert str(dog) == 'Pluto'


def test_valid_favourite_dog(db, today_date):
    dog = mixer.blend("dogs.Dog", birth_date=today_date, entry_date=today_date)
    user = mixer.blend("auth.User")

    favourite_dog = mixer.blend("dogs.FavouriteDog", user=user, dog=dog)
    assert favourite_dog.user == user and favourite_dog.dog == dog


def test_favourite_dog_to_str(db, today_date):
    dog = mixer.blend("dogs.Dog", birth_date=today_date, entry_date=today_date)
    user = mixer.blend("auth.User")

    favourite_dog = mixer.blend("dogs.FavouriteDog", user=user, dog=dog)
    assert str(favourite_dog) == f"{str(user)} - {str(dog)}"
