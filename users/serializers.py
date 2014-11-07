from rest_framework import serializers

from .models import User, UserGroup, GroupingUserGroup


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


class GroupingUserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for ViewGroup model.
    """
    class Meta:
        model = GroupingUserGroup
        fields = ('grouping', 'can_read', 'can_view')
