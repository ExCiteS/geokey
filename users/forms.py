from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, UserGroup


# class MyUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User


# class MyUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User

#     def clean_username(self):
#         username = self.cleaned_data["username"]
#         try:
#             User.objects.get(username=username)
#         except User.DoesNotExist:
#             return username
#         raise forms.ValidationError(self.error_messages['duplicate_username'])


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password', 'display_name')


class UsergroupCreateForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ('name', 'description')
