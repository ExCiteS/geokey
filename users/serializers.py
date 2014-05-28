from rest_framework import serializers

from .models import User, UserGroup, ViewUserGroup


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'display_name')


class UserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for project user groups.
    """
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        depth = 1
        fields = ('id', 'name', 'description', 'users', 'can_contribute')


class ViewGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewUserGroup
        fields = ('view', 'can_read', 'can_view', 'can_moderate')
