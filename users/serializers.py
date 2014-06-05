from rest_framework import serializers

from .models import User, UserGroup, ViewUserGroup


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'display_name')
        write_only_fields = ('email',)


class UserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for UserGroup model.
    """
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        depth = 1
        fields = (
            'id', 'name', 'description', 'users', 'can_contribute',
            'can_moderate'
        )


class ViewGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for ViewGroup model.
    """
    class Meta:
        model = ViewUserGroup
        fields = ('view', 'can_read', 'can_view')
