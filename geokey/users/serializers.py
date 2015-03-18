from rest_framework.serializers import ModelSerializer, ValidationError

from geokey.core.serializers import FieldSelectorSerializer
from .models import User, UserGroup, GroupingUserGroup


class UserSerializer(FieldSelectorSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'display_name')

    def validate_display_name(self, value):
        if User.objects.filter(display_name__iexact=value).exists():
            raise ValidationError('Display name already exists')

        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError('Email already exists')

        return value


class UserGroupSerializer(ModelSerializer):
    """
    Serializer for UserGroup model.
    """
    users = UserSerializer(many=True, fields=('id', 'display_name'))

    class Meta:
        model = UserGroup
        depth = 1
        fields = (
            'id', 'name', 'description', 'users', 'can_contribute',
            'can_moderate'
        )


class GroupingUserGroupSerializer(ModelSerializer):
    """
    Serializer for ViewGroup model.
    """
    class Meta:
        model = GroupingUserGroup
        fields = ('grouping', 'can_read', 'can_view')
