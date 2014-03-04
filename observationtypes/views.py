from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect

from braces.views import LoginRequiredMixin

from projects.models import Project
from core.decorators import (
    handle_exceptions_for_admin
)

from .models import ObservationType, STATUS
from .forms import ObservationTypeCreateForm


class ObservationTypeAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create ObservationType page and creates the ObservationType
    when POST is requested
    """
    form_class = ObservationTypeCreateForm
    template_name = 'observationtypes/observationtype_create.html'

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            ObservationTypeAdminCreateView, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, pk=project_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.
        """
        project_id = self.kwargs['project_id']

        data = form.cleaned_data
        project = Project.objects.as_admin(self.request.user, pk=project_id)

        observation_type = ObservationType.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            project=project
        )
        return redirect(
            'admin:observationtype_detail',
            project_id=project.id,
            observationtype_id=observation_type.id
        )


class ObservationTypeAdminDetailView(LoginRequiredMixin, TemplateView):
    """
    Displays the observation type detail page
    """
    template_name = 'observationtypes/observationtype_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, observationtype_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        project = Project.objects.as_admin(user, pk=project_id)
        return {
            'observationtype': project.observationtype_set.get(
                pk=observationtype_id),
            'admin': project.is_admin(user),
            'status_types': STATUS
        }
