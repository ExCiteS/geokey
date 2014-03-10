from django import forms

from .models import View, ViewGroup


class ViewCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ViewAdminCreateView
    """
    class Meta:
        model = View
        fields = ('name', 'description')


class ViewGroupCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ViewGroupAdminCreateView
    """
    class Meta:
        model = ViewGroup
        fields = ('name', 'description')
