from django import forms

from .models import ObservationType, Field


class ObservationTypeCreateForm(forms.ModelForm):
    class Meta:
        model = ObservationType
        fields = ('name', 'description')


class FieldCreateForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ('name', 'key', 'description', 'required')
