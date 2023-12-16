from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class RoleView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response({'role': 'doghouse-worker'}) if request.user.groups.filter(
            name='doghouse-workers').exists() else Response({'role': 'user'})
