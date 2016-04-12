"""Forms for projects."""

from django import forms

from .models import Project


class ProjectCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ProjectAdminCreateView
    """
    class Meta:
        model = Project
        fields = ('name', 'description', 'isprivate', 'islocked',
                  'everyone_contributes')
