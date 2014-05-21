from django import forms
from django.contrib.auth.models import User

from .models import UserGroup


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name',)


class UsergroupCreateForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ('name', 'description')
