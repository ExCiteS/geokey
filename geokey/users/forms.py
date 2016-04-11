"""Forms for users."""

from django import forms
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError

from allauth.account.forms import (
    ChangePasswordForm,
    ResetPasswordKeyForm,
    SignupForm
)

from oauth2_provider.models import AccessToken

from .models import User, UserGroup


class UserForm(forms.ModelForm):
    """
    Validates form fields against the User model definition.
    """
    class Meta:
        model = User
        fields = ['display_name', 'email']


class UserRegistrationForm(SignupForm):
    """
    Cleans data when users are signing up
    """
    display_name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        """
        Initialise

        Removes the username field
        """
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean(self):
        """
        Overwrites method to assign display_name value to username
        """
        self.cleaned_data['username'] = self.cleaned_data.get('display_name')
        return super(UserRegistrationForm, self).clean()

    def clean_display_name(self):
        """
        Cleans the display_name field. Checks if the user name exists and
        raises an exception if so.

        Returns
        -------
        str
            Cleaned display name

        Raises
        ------
        ValidationError
            if the display_name exisits
        """
        cleaned = self.cleaned_data.get('display_name')
        if User.objects.filter(display_name__iexact=cleaned).exists():
            raise ValidationError('The given display name exists.')

        return cleaned


class UsergroupCreateForm(forms.ModelForm):
    """
    Validates the inputs against the UserGroup model definition.
    Used in .views.UserGroupCreate
    """
    class Meta:
        model = UserGroup
        fields = ('name', 'description')

    def clean(self):
        """
        Removes HTML tags from name and desription

        Returns
        -------
        dict
            validated data
        """
        cleaned_data = super(UsergroupCreateForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])

        return cleaned_data


class CustomPasswordChangeForm(ChangePasswordForm):
    """
    Changes the password
    """
    def save(self, *args, **kwargs):
        """
        Saves the new password and returns the user. Deletes all OAuth access
        tokens assigned to the user.

        Returns
        -------
        geokey.users.models.User
            User who changed the password
        """
        user = super(CustomPasswordChangeForm, self).save(*args, **kwargs)
        AccessToken.objects.filter(user=user).delete()
        return user


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    """
    Resets the password
    """
    def save(self, *args, **kwargs):
        """
        Excecutes the password reset. Deletes all OAuth access tokens assigned
        to the user.
        """
        AccessToken.objects.filter(user=self.user).delete()
        super(CustomResetPasswordKeyForm, self).save(*args, **kwargs)
