import datetime
import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from mixer.backend.django import mixer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_304_NOT_MODIFIED, \
    HTTP_204_NO_CONTENT, HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.test import APIClient
import json


def get_client(user=None):
    res = APIClient()
    if user is not None:
        res.force_login(user)
    return res


def parse(response):
    response.render()
    content = response.content.decode()
    return json.loads(content)


def get_role_response(user=None):
    path = reverse('get-role')
    client = get_client(user)

    response = client.get(path, format='json')
    return response


def test_get_role_user_is_worker(db):
    user = mixer.blend("auth.User")
    group = mixer.blend('auth.Group', name='doghouse-workers')
    user.groups.set([group])

    response = get_role_response(user)
    obj = parse(response)

    assert response.status_code == HTTP_200_OK and obj['role'] == 'doghouse-worker'


def test_get_role_user_not_worker(db):
    user = mixer.blend("auth.User")
    user.groups.set([])

    response = get_role_response(user)
    obj = parse(response)

    assert response.status_code == HTTP_200_OK and obj['role'] == 'user'


def test_get_role_user_not_authenticated():
    assert get_role_response().status_code == HTTP_403_FORBIDDEN

