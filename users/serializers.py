from django.contrib.auth.models import User

from rest_framework import serializers

from .models import UserGroup


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for project user groups.
    """
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        depth = 1
        fields = ('id', 'name', 'description', 'users')
