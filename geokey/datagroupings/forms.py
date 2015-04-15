from django import forms
from django.utils.html import strip_tags

from .models import Grouping


class GroupingCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ViewAdminCreateView
    """
    class Meta:
        model = Grouping
        fields = ('name', 'description', 'isprivate')

    def clean(self):
        """
        Cleans incoming data and returnes cleaned data. Removes HTML tags from
        name and description.

        Return
        ------
        dict
            Cleaned form data.
        """
        cleaned_data = super(GroupingCreateForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])

        return cleaned_data
