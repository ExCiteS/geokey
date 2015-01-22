from django import forms
from django.utils.html import strip_tags
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError

from oauth2_provider.models import AccessToken

from .models import User, UserGroup


class UserRegistrationForm(forms.ModelForm):
    """
    Validates the inputs against the User model definition.
    Used in .views.Signup
    """
    class Meta:
        model = User
        fields = ('email', 'password', 'display_name')

    def clean_display_name(self):
        cleaned = self.cleaned_data.get('display_name')
        if self.instance is None or self.instance.display_name != cleaned:
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


class CustomPasswordChangeForm(SetPasswordForm):
    def save(self, *args, **kwargs):
        user = super(CustomPasswordChangeForm, self).save(*args, **kwargs)
        AccessToken.objects.filter(user=user).delete()
        return user
