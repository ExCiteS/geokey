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


class UserRegistrationForm(SignupForm):
    display_name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean(self):
        self.cleaned_data['username'] = self.cleaned_data.get('display_name')
        return super(UserRegistrationForm, self).clean()

    def clean_display_name(self):
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
        cleaned_data = super(UsergroupCreateForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])

        return cleaned_data


class CustomPasswordChangeForm(ChangePasswordForm):
    def save(self, *args, **kwargs):
        user = super(CustomPasswordChangeForm, self).save(*args, **kwargs)
        AccessToken.objects.filter(user=user).delete()
        return user


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def save(self, *args, **kwargs):
        AccessToken.objects.filter(user=self.user).delete()
        super(CustomResetPasswordKeyForm, self).save(*args, **kwargs)
