from django import forms

from .models import User, UserGroup


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password', 'display_name')


class UsergroupCreateForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ('name', 'description')
