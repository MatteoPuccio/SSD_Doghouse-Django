from django.contrib.auth.models import Group
from rest_framework import permissions

doghouse_workers_group = Group.objects.get_or_create(name='doghouse-workers')


class IsDoghouseWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name="doghouse-workers").exists()
