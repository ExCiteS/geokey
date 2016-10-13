"""Serializers for users."""

from allauth.socialaccount.models import SocialAccount
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework import serializers

from geokey.core.serializers import FieldSelectorSerializer
from .models import User, UserGroup


class SocialAccountSerializer(FieldSelectorSerializer):
    """
    Serializer for SocialAccount model.
    """

    class Meta:
        model = SocialAccount
        fields = ('id', 'provider')


class UserSerializer(FieldSelectorSerializer):
    """
    Serializer for User model.
    """

    social_accounts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'display_name','social_accounts')

    def get_social_accounts(self, value):
        """
        Get social account information for the user.

        Parameters
        ----------
        value : str
            Display name to be examined.

        Returns
        -------
        list
            The social account information.
        """
        serializer = SocialAccountSerializer(
            value.socialaccount_set.all(), many=True)
        return serializer.data

    def validate_display_name(self, value):
        """
        Check if the display name already exists.

        Parameters
        ----------
        value : str
            Display name to be examined.

        Returns
        -------
        str
            The display name.

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
