import datetime
import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from mixer.backend.django import mixer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_304_NOT_MODIFIED, \
    HTTP_204_NO_CONTENT
from rest_framework.test import APIClient
import json

from dogs.models import Dog
from dogs.serializers import DogSerializer


@pytest.fixture()
def yesterday_date():
    return datetime.date.today() - datetime.timedelta(days=1)


@pytest.fixture()
def today_date():
    return datetime.date.today()


@pytest.fixture()
def dogs(db):
    return [
        mixer.blend('dogs.Dog'),
        mixer.blend('dogs.Dog'),
        mixer.blend('dogs.Dog'),
    ]


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


def test_anon_user_get_dog_details(db):
    dog = mixer.blend('dogs.Dog')
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

    print(response)

    assert (response.status_code == HTTP_204_NO_CONTENT
            and not Dog.objects.filter(id=data['id']).exists())


def test_not_authorized_delete_dog(db):
    user = mixer.blend('auth.User')
    user.groups.set([])

    data, response = delete_dog_response(user)

    assert (response.status_code == HTTP_403_FORBIDDEN and Dog.objects.filter(id=data['id']).exists())

