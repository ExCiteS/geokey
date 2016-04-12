"""Forms for categories."""

from django import forms

from .models import Category, Field


class CategoryCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ObservationTypeAdminCreateView
    """

    class Meta:
        model = Category
        fields = ('name', 'description', 'default_status')


class FieldCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.FieldAdminCreateView
    """
    class Meta:
        model = Field
        fields = ('name', 'description', 'required')
