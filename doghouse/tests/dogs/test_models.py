import datetime

import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
import dogs.models


def test_name_length_21_chars_raises_exception(db):
    dog = mixer.blend('dogs.Dog', name='A' * 21)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_name_length_1_chars_raises_exception(db):
    dog = mixer.blend('dogs.Dog', name='A')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_name_no_name_equals_unnamed(db):
    dog = dogs.models.Dog()
    assert dog.name == 'Unnamed'


@pytest.mark.parametrize('name', ['g4nz0', 'dragonball$', '<alert>'])
def test_name_containing_invalid_chars_raises_exception(db, name):
    dog = mixer.blend('dogs.Dog', name=name)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_breed_not_in_dogs_breed_json_raises_exception(db):
    dog = mixer.blend('dogs.Dog', breed='Cheems')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_sex_not_valid_raises_exception(db):
    dog = mixer.blend('dogs.Dog', sex='Xrlg')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_birth_date_earlier_than_1980_raises_exception(db):
    date = datetime.date(1979, 1, 24)
    dog = mixer.blend('dogs.Dog', birth_date=date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_birth_date_older_than_today_raises_exception(db):
    date = datetime.date.today() + datetime.timedelta(days=1)
    dog = mixer.blend('dogs.Dog', birth_date=date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_entry_date_earlier_than_1980_raises_exception(db):
    date = datetime.date(1979, 1, 24)
    dog = mixer.blend('dogs.Dog', entry_date=date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_entry_date_older_than_today_raises_exception(db):
    date = datetime.date.today() + datetime.timedelta(days=1)
    dog = mixer.blend('dogs.Dog', entry_date=date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_description_longer_than_400_chars_raises_exception(db):
    dog = mixer.blend('dogs.Dog', description='A' * 401)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('description', ['dog$', '/1)cn', '(&~', '<alert>'])
def test_description_containing_invalid_chars_raises_exception(db, description):
    dog = mixer.blend('dogs.Dog', description=description)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_description_containing_special_characters(db):
    description = ';,.!? 1-\t'
    dog = mixer.blend('dogs.Dog', description=description)
    assert dog.description == description


def test_estimated_adult_size_not_in_dict_raises_exception(db):
    dog = mixer.blend('dogs.Dog', estimated_size='XXXXL')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_picture_not_proper_url_raises_exception(db):
    dog = mixer.blend('dogs.Dog', picture='httpee://///error')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()
