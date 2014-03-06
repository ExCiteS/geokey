from django import forms

from .models import View


class ViewCreateForm(forms.ModelForm):
    class Meta:
        model = View
        fields = ('name', 'description')
