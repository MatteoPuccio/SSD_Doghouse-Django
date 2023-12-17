import datetime
import pytest
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient
import json

from dogs.models import Dog, FavouriteDog
from dogs.serializers import DogSerializer


@pytest.fixture()
def yesterday_date():
    return datetime.date.today() - datetime.timedelta(days=1)


@pytest.fixture()
def today_date():
    return datetime.date.today()


@pytest.fixture()
def dogs(db, today_date, yesterday_date):
    return [mixer.blend('dogs.Dog', birth_date=yesterday_date, entry_date=today_date) for _ in range(3)]


@pytest.fixture()
def user(db):
    return mixer.blend('auth.User')


def get_client(user=None):
    res = APIClient()
    if user is not None:
        res.force_login(user)
    return res


def parse(response):
    response.render()
    content = response.content.decode()
    return json.loads(content)


def add_dog_response(user=None):
    path = reverse('dogs-list')
    client = get_client(user)

    dog = mixer.blend("dogs.Dog", birth_date=datetime.date.today() - datetime.timedelta(days=1),
                      entry_date=datetime.date.today())
    serializer = DogSerializer(dog)
    data = serializer.data

    response = client.post(path, data=data, format='json')
    return data, response


def edit_dog_response(user=None):
    dog = mixer.blend("dogs.Dog", name='Before', birth_date=datetime.date.today() - datetime.timedelta(days=1),
                      entry_date=datetime.date.today())

    path = reverse('dogs-detail', kwargs={'pk': dog.id})
    client = get_client(user)

    serializer = DogSerializer(dog)
    data = serializer.data
    data['name'] = 'After'

    response = client.put(path, data=data, format='json')
    return data, response


def delete_dog_response(user=None):
    dog = mixer.blend("dogs.Dog", birth_date=datetime.date.today() - datetime.timedelta(days=1),
                      entry_date=datetime.date.today())

    path = reverse('dogs-detail', kwargs={'pk': dog.id})
    client = get_client(user)

    serializer = DogSerializer(dog)
    data = serializer.data

    response = client.delete(path, data=data, format='json')
    return data, response


def test_anon_user_get_dog_list(dogs):
    path = reverse('dogs-list')
    client = get_client()
    response = client.get(path)
    assert response.status_code == HTTP_200_OK
    obj = parse(response)
    assert len(obj) == len(dogs)


def test_anon_user_get_dog_details(db, today_date, yesterday_date):
    dog = mixer.blend('dogs.Dog', birth_date=yesterday_date, entry_date=today_date)
    path = reverse('dogs-detail', kwargs={'pk': dog.pk})
    client = get_client()
    response = client.get(path)
    assert response.status_code == HTTP_200_OK
    obj = parse(response)
    assert obj['id'] == dog.id


def test_doghouse_workers_add_dog(db, user):
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    data, response = add_dog_response(user)

    obj = parse(response)
    del obj['id']
    del data['id']

    assert (response.status_code == HTTP_201_CREATED
            and obj == data)


def test_not_authorized_add_dog_forbidden(db, user):
    user.groups.set([])

    data, response = add_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN)


def test_doghouse_worker_edit_dog(db, user):
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    data, response = edit_dog_response(user)

    obj = parse(response)

    assert (response.status_code == HTTP_200_OK
            and obj == data)


def test_not_authorized_edit_dog(db, user):
    user.groups.set([])

    data, response = edit_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN)


def test_doghouse_worker_delete_dog(db, user):
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    data, response = delete_dog_response(user)

    assert (response.status_code == HTTP_204_NO_CONTENT
            and not Dog.objects.filter(id=data['id']).exists())


def test_not_authorized_delete_dog(db, user):
    user.groups.set([])

    data, response = delete_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN and Dog.objects.filter(id=data['id']).exists())


def test_list_favourite_dogs(db, dogs, user):
    for dog in dogs:
        mixer.blend('dogs.FavouriteDog', user=user, dog=dog)

    path = reverse('favourite-dogs-list')
    client = get_client(user)

    response = client.get(path)
    obj = parse(response)

    assert response.status_code == HTTP_200_OK and len(dogs) == len(obj)

    serializer = DogSerializer(dogs, many=True)
    for entry in obj:
        assert entry['dog'] in serializer.data


def test_list_favourite_dogs_not_authenticated(db):
    path = reverse('favourite-dogs-list')
    client = get_client()
    response = client.get(path)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_get_favourite_dog(db, dogs, user):
    mixer.blend('dogs.FavouriteDog', user=user, dog=dogs[0])

    path = reverse('favourite-dogs-detail', kwargs={'dog_id': dogs[0].pk})
    client = get_client(user)

    response = client.get(path)
    obj = parse(response)

    serializer = DogSerializer(dogs[0])

    assert response.status_code == HTTP_200_OK and obj['dog'] == serializer.data


def test_get_favourite_dog_not_authenticated(db):
    path = reverse('favourite-dogs-detail', kwargs={'dog_id': 1})
    client = get_client()

    response = client.get(path)
    assert response.status_code == HTTP_403_FORBIDDEN


def test_get_favourite_dog_id_not_in_favourites(db, user):
    path = reverse('favourite-dogs-detail', kwargs={'dog_id': 1})
    client = get_client(user)

    response = client.get(path)
    assert response.status_code == HTTP_404_NOT_FOUND


def test_add_dog_to_favourite_dogs(db, dogs, user):
    path = reverse('favourite-dogs-list')
    client = get_client(user)

    serializer = DogSerializer(dogs[0])
    response = client.post(path, data={'dog_id': serializer.data['id']}, format="json")
    assert response.status_code == HTTP_201_CREATED and FavouriteDog.objects.filter(user=user, dog=dogs[0]).exists()


def test_add_dog_to_favourite_dogs_not_authenticated(db):
    path = reverse('favourite-dogs-list')
    client = get_client()

    response = client.post(path)
    assert response.status_code == HTTP_403_FORBIDDEN


def test_add_dog_to_favourite_dogs_already_in_favourites(db, dogs, user):
    path = reverse('favourite-dogs-list')
    client = get_client(user)

    serializer = DogSerializer(dogs[0])

    mixer.blend('dogs.FavouriteDog', user=user, dog=dogs[0])

    response = client.post(path, data={'dog_id':serializer.data['id']}, format="json")
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_query_dogs_by_breed(db, today_date, user):
    dog1 = mixer.blend('dogs.Dog', breed='Spinone Italiano', birth_date=today_date, entry_date=today_date)
    dog2 = mixer.blend('dogs.Dog', breed='Yorkshire Terrier', birth_date=today_date, entry_date=today_date)

    path = reverse('dogs-list') + '?breed=Spinone Italiano'
    client = get_client(user)

    response = client.get(path)
    obj = parse(response)

    dog1_json = DogSerializer(dog1).data
    dog2_json = DogSerializer(dog2).data

    print(obj)

    assert response.status_code == HTTP_200_OK and dog1_json in obj and dog2_json not in obj


def test_query_dogs_by_estimated_adult_size(db, today_date, user):
    dog1 = mixer.blend('dogs.Dog', estimated_adult_size='L', birth_date=today_date, entry_date=today_date)
    dog2 = mixer.blend('dogs.Dog', estimated_adult_size='XL', birth_date=today_date, entry_date=today_date)

    path = reverse('dogs-list') + '?estimated_adult_size=L'
    client = get_client(user)

    response = client.get(path)
    obj = parse(response)

    dog1_json = DogSerializer(dog1).data
    dog2_json = DogSerializer(dog2).data

    assert response.status_code == HTTP_200_OK and dog1_json in obj and dog2_json not in obj


def test_query_dogs_by_birth_date(db, today_date, user):
    dog1 = mixer.blend('dogs.Dog', birth_date=datetime.date(2011, 12, 2), entry_date=today_date)
    dog2 = mixer.blend('dogs.Dog', birth_date=datetime.date(2013, 1, 15), entry_date=today_date)
    dog3 = mixer.blend('dogs.Dog', birth_date=datetime.date(2018, 5, 26), entry_date=today_date)
    dog4 = mixer.blend('dogs.Dog', birth_date=datetime.date(2020, 8, 21), entry_date=today_date)

    path = reverse('dogs-list') + '?birth_date_gte=2013' + '&birth_date_lte=2019'
    client = get_client(user)

    response = client.get(path)
    obj = parse(response)

    dog1_json = DogSerializer(dog1).data
    dog2_json = DogSerializer(dog2).data
    dog3_json = DogSerializer(dog3).data
    dog4_json = DogSerializer(dog4).data

    assert response.status_code == HTTP_200_OK and dog2_json in obj and dog3_json in obj \
           and dog1_json not in obj and dog4_json not in obj
