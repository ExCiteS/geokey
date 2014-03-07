from django import forms

from .models import View, ViewGroup


class ViewCreateForm(forms.ModelForm):
    class Meta:
        model = View
        fields = ('name', 'description')


class ViewGroupCreateForm(forms.ModelForm):
    class Meta:
        model = ViewGroup
        fields = ('name', 'description')
