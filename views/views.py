from django.views.generic import CreateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from projects.models import Project

from .forms import ViewCreateForm
from .models import View


class ViewAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create project page
    """
    form_class = ViewCreateForm
    template_name = 'views/view_create.html'

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        return reverse('admin:project_settings', kwargs={'project_id': project_id})

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            ViewAdminCreateView, self).get_context_data(**kwargs)

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
        project = Project.objects.as_admin(self.request.user, pk=project_id)

        form.instance.project = project
        form.instance.creator = self.request.user
        return super(ViewAdminCreateView, self).form_valid(form)
