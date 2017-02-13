"""Forms for applications."""

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
        fields = ('name', 'description', 'download_url', 'redirect_uris',
                  'authorization_grant_type', 'skip_authorization')

    def clean(self):
        """
        Overwrites ModelForm's clean method to strip HTML Tags from name and
        description

        Returns
        -------
        dict
            Cleaned form data including HTML free name and description
        """
        cleaned_data = super(AppCreateForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])

        return cleaned_data
