from rest_framework import serializers

from core.serializers import FieldSelectorSerializer
from users.serializers import UserSerializer
from dataviews.serializers import ViewSerializer
from observationtypes.serializer import ObservationTypeSerializer

from .models import Project, UserGroup


class UserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for project user groups.
    """
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        depth = 1
        fields = ('id', 'name', 'users')


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for projects.
    """
    views = ViewSerializer(read_only=True, many=True)
    observationtypes = ObservationTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'everyonecontributes', 'created_at', 'views',
                  'observationtypes')
        read_only_fields = ('id', 'name')
