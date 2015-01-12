from django import forms

from .models import Application
from django.utils.html import strip_tags


class AppCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.AppCreateView
    """
    class Meta:
        model = Application
        fields = ('name', 'description', 'download_url', 'redirect_uris')

    def clean(self):
        cleaned_data = super(AppCreateForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])

        return cleaned_data
