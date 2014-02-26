from django.db.models import Q
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer


class QueryUsers(APIView):
    def get(self, request, format=None):
        q = request.GET.get('query').lower()
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(last_name__icontains=q) |
            Q(first_name__icontains=q))[:10]

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
