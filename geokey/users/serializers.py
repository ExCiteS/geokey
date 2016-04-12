"""Serializers for users."""

from rest_framework.serializers import ModelSerializer, ValidationError

from geokey.core.serializers import FieldSelectorSerializer
from .models import User, UserGroup


class UserSerializer(FieldSelectorSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'display_name')

    def validate_display_name(self, value):
        """
        Checks if the display name already exists

        Parameter
        ---------
        value : str
            Display name to be examined

        Returns
        -------
        str
            The display name

        Raises
        ------
        ValidationError
            If the display name exists in the data base
        """
        if User.objects.filter(display_name__iexact=value).exists():
            raise ValidationError('Display name already exists')

        return value

    def validate_email(self, value):
        """
        Checks if the email already exists

        Parameter
        ---------
        value : str
            email to be examined

        Returns
        -------
        str
            The email

        Raises
        ------
        ValidationError
            If the email exists in the data base
        """
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
