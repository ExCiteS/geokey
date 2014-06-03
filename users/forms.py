from django import forms

from .models import User, UserGroup


class UserRegistrationForm(forms.ModelForm):
    """
    Validates the inputs against the User model definition.
    Used in .views.Signup
    """
    class Meta:
        model = User
        fields = ('email', 'password', 'display_name')


class UsergroupCreateForm(forms.ModelForm):
    """
    Validates the inputs against the UserGroup model definition.
    Used in .views.UserGroupCreate
    """
    class Meta:
        model = UserGroup
        fields = ('name', 'description')
