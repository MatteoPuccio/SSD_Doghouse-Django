import datetime
import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from mixer.backend.django import mixer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient
import json

from dogs.models import Dog
from dogs.serializers import DogSerializer
from dogs.views import FavouriteDogsView


@pytest.fixture()
def yesterday_date():
    return datetime.date.today() - datetime.timedelta(days=1)


@pytest.fixture()
def today_date():
    return datetime.date.today()


@pytest.fixture()
def dogs(db, today_date, yesterday_date):
    return [mixer.blend('dogs.Dog', birth_date=yesterday_date, entry_date=today_date) for _ in range(3)]


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


def add_dog_to_user_interested(user=None):
    dog = mixer.blend("dogs.Dog", birth_date=datetime.date.today() - datetime.timedelta(1),
                      entry_date=datetime.date.today())
    path = reverse('favourite-dogs')
    client = get_client(user)

    serializer = DogSerializer(dog)
    data = serializer.data

    response = client.post(path, data=data, format='json')
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


def test_doghouse_workers_add_dog(db):
    user = mixer.blend('auth.User')
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    data, response = add_dog_response(user)

    obj = parse(response)
    del obj['id']
    del data['id']

    assert (response.status_code == HTTP_201_CREATED
            and obj == data)


def test_not_authorized_add_dog_forbidden(db):
    user = mixer.blend('auth.User')
    user.groups.set([])

    data, response = add_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN)


def test_doghouse_worker_edit_dog(db):
    user = mixer.blend('auth.User')
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    data, response = edit_dog_response(user)

    obj = parse(response)

    assert (response.status_code == HTTP_200_OK
            and obj == data)


def test_not_authorized_edit_dog(db):
    user = mixer.blend('auth.User')
    user.groups.set([])

    data, response = edit_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN)


def test_doghouse_worker_delete_dog(db):
    user = mixer.blend('auth.User')
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    data, response = delete_dog_response(user)

    assert (response.status_code == HTTP_204_NO_CONTENT
            and not Dog.objects.filter(id=data['id']).exists())


def test_not_authorized_delete_dog(db):
    user = mixer.blend('auth.User')
    user.groups.set([])

    data, response = delete_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN and Dog.objects.filter(id=data['id']).exists())


def test_add_dog_to_user_interested_list(db):
    user = mixer.blend('auth.User')

    data, response = add_dog_to_user_interested(user)

    assert (response.status_code == HTTP_200_OK and Dog.objects.filter(id=data['id']).get().interested_users.filter(
        id=user.id).exists())


def test_add_dog_to_user_interested_list_not_authenticated(db):
    _, response = add_dog_to_user_interested()

    assert (response.status_code == HTTP_403_FORBIDDEN)


def test_add_dog_to_user_interested_list_id_not_present_in_db(db):
    user = mixer.blend('auth.User')

    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.post(path, data={'id': -1}, format='json')
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj[
        'message'] == FavouriteDogsView.DOG_NOT_FOUND_MESSAGE


def test_add_dog_to_user_interested_list_id_not_integer(db):
    user = mixer.blend('auth.User')

    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.post(path, data={'id': "enfbje"}, format='json')
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj['message'] == FavouriteDogsView.ID_NOT_INT_MESSAGE


def test_add_dog_to_user_interested_list_id_not_present_in_request(db):
    user = mixer.blend('auth.User')

    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.post(path)
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj['message'] == FavouriteDogsView.ABSENT_ID_MESSAGE


def test_add_dog_to_user_interested_list_dog_already_added(db, dogs):
    user = mixer.blend('auth.User')
    dog = dogs[0]
    dog.interested_users.add(user)

    path = reverse('favourite-dogs')
    client = get_client(user)

    serializer = DogSerializer(dog)

    response = client.post(path, data=serializer.data, format='json')
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj[
        'message'] == FavouriteDogsView.DOG_ALREADY_IN_FAVOURITES_MESSAGE


def test_get_dogs_from_user_interested_list(db, dogs):
    user = mixer.blend('auth.User')
    for dog in dogs:
        dog.interested_users.add(user)

    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.get(path)
    obj = parse(response)

    serializer = DogSerializer(dogs, many=True)

    assert response.status_code == HTTP_200_OK and len(dogs) == len(obj['favourite-dogs'])

    for dog in serializer.data:
        assert dog in obj['favourite-dogs']


def test_get_dogs_from_user_interested_list_not_authenticated(db):
    path = reverse('favourite-dogs')
    client = get_client()

    response = client.get(path)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_delete_dog_from_user_interested_list(db, dogs):
    user = mixer.blend('auth.User')
    dog = dogs[0]
    dog.interested_users.add(user)

    path = reverse('favourite-dogs')
    client = get_client(user)

    serializer = DogSerializer(dog)

    response = client.delete(path, data=serializer.data, format='json')
    assert response.status_code == HTTP_200_OK and not dog.interested_users.filter(id=user.id).exists()


def test_delete_dog_from_user_interested_list_not_authenticated(db):
    path = reverse('favourite-dogs')
    client = get_client()

    response = client.delete(path)
    assert response.status_code == HTTP_403_FORBIDDEN


def test_delete_dog_from_user_interested_list_id_not_present_in_db(db):
    user = mixer.blend('auth.User')
    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.delete(path, data={'id': -1}, format='json')
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj[
        'message'] == FavouriteDogsView.DOG_NOT_FOUND_MESSAGE


def test_delete_dog_from_user_interested_list_id_not_integer(db):
    user = mixer.blend('auth.User')
    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.delete(path, data={'id': "jebkwbtjke"}, format='json')
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj['message'] == FavouriteDogsView.ID_NOT_INT_MESSAGE


def test_delete_dog_from_user_interested_list_id_not_present_in_request(db):
    user = mixer.blend('auth.User')
    path = reverse('favourite-dogs')
    client = get_client(user)

    response = client.delete(path)
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj['message'] == FavouriteDogsView.ABSENT_ID_MESSAGE


def test_delete_dog_from_user_interested_list_id_not_present_in_user_favourites(db, dogs):
    user = mixer.blend('auth.User')

    path = reverse('favourite-dogs')
    client = get_client(user)

    serializer = DogSerializer(dogs[0])

    response = client.delete(path, data=serializer.data, format='json')
    obj = parse(response)

    assert response.status_code == HTTP_400_BAD_REQUEST and obj[
        'message'] == FavouriteDogsView.DOG_NOT_IN_FAVOURITES_MESSAGE
