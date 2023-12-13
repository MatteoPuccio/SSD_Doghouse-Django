import datetime

import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from dogs.models import Dog, picture_source_prefix


@pytest.mark.parametrize('name', ['Pluto', 'Goku', 'Pochita'])
def test_valid_dog_name(db, name):
    dog = mixer.blend('dogs.Dog', name=name)
    assert dog.name == name


def test_dog_not_start_uppercase(db):
    dog = mixer.blend('dogs.Dog', name='pluto')
    with pytest.raises(ValidationError):
        dog.full_clean()


def test_dog_uppercase_in_middle(db):
    dog = mixer.blend('dogs.Dog', name='plUto')
    with pytest.raises(ValidationError):
        dog.full_clean()


def test_name_length_21_chars_raises_exception(db):
    dog = mixer.blend('dogs.Dog', name='A' * 21)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_name_length_1_chars_raises_exception(db):
    dog = mixer.blend('dogs.Dog', name='A')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_name_no_name_equals_unnamed(db):
    dog = mixer.blend('dogs.Dog')
    assert dog.name == 'Unnamed'


@pytest.mark.parametrize('name', ['g4nz0', 'dragonball$', '<alert>'])
def test_name_containing_invalid_chars_raises_exception(db, name):
    dog = mixer.blend('dogs.Dog', name=name)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('breed', ['American Hairless Terrier', 'Dutch Shepherd Dog',
                                   'Great Dane', 'Spanish Mastiff'])
def test_valid_breed(db, breed):
    dog = mixer.blend('dogs.Dog', breed=breed)
    assert dog.breed == breed


def test_breed_not_in_dogs_breed_json_raises_exception(db):
    dog = mixer.blend('dogs.Dog', breed='Cheems')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('sex', ['M', 'F'])
def test_valid_sex(db, sex):
    dog = mixer.blend('dogs.Dog', sex=sex)
    assert dog.sex == sex


def test_sex_not_valid_raises_exception(db):
    dog = mixer.blend('dogs.Dog', sex='Xrlg')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('birth_date', [datetime.date(2005, 12, 31),
                                        datetime.date(2008, 1, 24),
                                        datetime.date(2011, 5, 11)])
def test_valid_birth_date(db, birth_date):
    dog = mixer.blend('dogs.Dog', birth_date=birth_date)
    assert dog.birth_date == birth_date


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


@pytest.mark.parametrize('entry_date', [datetime.date(2005, 12, 31),
                                        datetime.date(2008, 1, 24),
                                        datetime.date(2011, 5, 11)])
def test_valid_entry_date(db, entry_date):
    dog = mixer.blend('dogs.Dog', entry_date=entry_date)
    assert dog.entry_date == entry_date


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


def test_entry_date_earlier_than_birth_date_raises_exception(db):
    entry_date = datetime.date.today() - datetime.timedelta(days=1)
    birth_date = datetime.date.today()
    dog = mixer.blend('dogs.Dog', entry_date=entry_date, birth_date=birth_date)
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_neutered_exists(db):
    dog = mixer.blend('dogs.Dog')
    assert dog.neutered is not None


@pytest.mark.parametrize('description', ['Lorem ipsum dolor sit amet, consectetur adipiscing elit',
                                         'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                                         'Ut enim ad minim veniam, quis nostrud exercitation ullamco',
                                         '',
                                         None])
def test_valid_description(db, description):
    dog = mixer.blend('dogs.Dog', description=description)
    assert dog.description == description


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


@pytest.mark.parametrize('estimated_adult_size', ['XS', 'S', 'M', 'L', 'XL'])
def test_valid_estimated_adult_size(db, estimated_adult_size):
    dog = mixer.blend('dogs.Dog', estimated_adult_size=estimated_adult_size)
    assert dog.estimated_adult_size == estimated_adult_size


def test_estimated_adult_size_not_in_dict_raises_exception(db):
    dog = mixer.blend('dogs.Dog', estimated_adult_size='XXXXL')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


@pytest.mark.parametrize('picture', [picture_source_prefix + 'x.png',
                                     picture_source_prefix + 'c.jpeg',
                                     picture_source_prefix + 'test.gif',
                                     None, ''])
def test_valid_picture(db, picture):
    dog = mixer.blend('dogs.Dog', picture=picture)
    assert dog.picture == picture


def test_picture_not_from_source_raises_exception(db):
    dog = mixer.blend('dogs.Dog', picture='https://example.com')
    with pytest.raises(ValidationError) as err:
        dog.full_clean()


def test_picture_length_201_raises_exception(db):
    picture = 'A' * (201 - len(picture_source_prefix))
    print(picture_source_prefix + picture)
    dog = mixer.blend('dogs.Dog', picture=picture_source_prefix + picture)
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
    user = mixer.blend('auth.User')

    dog = mixer.blend('dogs.Dog', name=name, breed=breed, sex=sex,
                      birth_date=birth_date,
                      entry_date=entry_date,
                      neutered=neutered,
                      description=description,
                      estimated_adult_size=estimated_adult_size,
                      picture=picture
                      )
    dog.interested_users.set([user])

    assert dog.name == name and dog.breed == breed and dog.sex == sex \
           and dog.birth_date == birth_date \
           and dog.entry_date == entry_date \
           and dog.neutered == neutered and dog.description == description \
           and dog.estimated_adult_size == estimated_adult_size and dog.picture == picture \
           and dog.interested_users.filter(id=user.id).exists()


def test_to_str(db):
    dog = mixer.blend('dogs.Dog', name='Pluto')
    assert str(dog) == 'Pluto'


def test_users_in_interested_users(db):
    user1 = mixer.blend('auth.User')
    user2 = mixer.blend('auth.User')
    user3 = mixer.blend('auth.User')

    dog = mixer.blend('dogs.Dog')
    dog.interested_users.set([user1, user2])
    assert dog.interested_users.filter(id=user1.id).exists() and dog.interested_users.filter(
        id=user2.id).exists() and not dog.interested_users.filter(id=user3.id).exists()
