from django import forms

from .models import Application


class AppCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.AppCreateView
    """
    class Meta:
        model = Application
        fields = ('name', 'description', 'download_url', 'redirect_url')
