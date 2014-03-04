from django import forms

from .models import ObservationType


class ObservationTypeCreateForm(forms.ModelForm):
    class Meta:
        model = ObservationType
        fields = ('name', 'description')
