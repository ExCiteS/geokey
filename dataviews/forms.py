from django import forms

from .models import View


class ViewCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ViewAdminCreateView
    """
    class Meta:
        model = View
        fields = ('name', 'description', 'ispublic')
