from django import forms

from .models import ObservationType, Field


class ObservationTypeCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ObservationTypeAdminCreateView
    """
    create_grouping = forms.CharField()

    class Meta:
        model = ObservationType
        fields = ('name', 'description', 'default_status')


class FieldCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.FieldAdminCreateView
    """
    class Meta:
        model = Field
        fields = ('name', 'description', 'required')
