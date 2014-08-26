import json

from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project
from observationtypes.models import ObservationType
from contributions.serializers import ContributionSerializer

from .base import STATUS
from .forms import ViewCreateForm
from .models import View, Rule
from .serializers import ViewSerializer


# ############################################################################
#
# Administration views
#
# ############################################################################

class ViewCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create view page
    """
    form_class = ViewCreateForm
    template_name = 'views/view_create.html'

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:view_settings',
            kwargs={'project_id': project_id, 'view_id': self.object.id}
        )

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            ViewCreate, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, project_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project
        form.instance.creator = self.request.user
        return super(ViewCreate, self).form_valid(form)


class ViewSettings(LoginRequiredMixin, TemplateView):
    template_name = 'views/view_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        view = View.objects.as_admin(user, project_id, view_id)
        return {'view': view, 'status_types': STATUS}

    def dispatch(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        view_id = kwargs.get('view_id')
        try:
            View.objects.as_admin(request.user, project_id, view_id)
        except PermissionDenied:
            return redirect(reverse('admin:view_observations', kwargs={
                'project_id': project_id,
                'view_id': view_id
            }))

        return super(ViewSettings, self).dispatch(
            request, *args, **kwargs)


class ViewAllSettings(LoginRequiredMixin, TemplateView):
    template_name = 'views/view_all_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        project = Project.objects.as_admin(user, project_id)
        return {'project': project}


class RuleCreate(LoginRequiredMixin, CreateView):
    """
    Displays the rule create page
    """
    template_name = 'views/view_rule_create.html'
    model = Rule

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Returns the context data for creating the view.
        """
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']

        context = super(
            RuleCreate, self).get_context_data(**kwargs)

        context['view'] = View.objects.as_admin(
            self.request.user, project_id, view_id
        )
        return context

    @handle_exceptions_for_admin
    def post(self, request, project_id, view_id):
        """
        Creates a new Rule with the POSTed data.
        """
        view = View.objects.as_admin(self.request.user, project_id, view_id)
        observation_type = ObservationType.objects.as_admin(
            self.request.user, project_id, request.POST.get('observationtype'))

        rules = None
        min_date = None
        max_date = None
        try:
            rules = json.loads(request.POST.get('rules', None))
            min_date = rules.pop('min_date')
            max_date = rules.pop('max_date')
        except ValueError:
            pass

        Rule.objects.create(
            view=view,
            observation_type=observation_type,
            min_date=min_date,
            max_date=max_date,
            filters=rules
        )

        return redirect('admin:view_settings',
                        project_id=project_id, view_id=view_id)


class RuleSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the settings page
    """
    template_name = 'views/view_rule_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id, rule_id, **kwargs):
        """
        Creates the request context for rendering the page
        """
        view = View.objects.as_admin(self.request.user, project_id, view_id)
        context = super(RuleSettings, self).get_context_data(**kwargs)

        context['rule'] = view.rules.get(pk=rule_id)
        return context

    @handle_exceptions_for_admin
    def post(self, request, project_id, view_id, rule_id):
        view = View.objects.as_admin(self.request.user, project_id, view_id)
        rule = view.rules.get(pk=rule_id)

        rules = json.loads(request.POST.get('rules'))

        rule.min_date = rules.pop('min_date')
        rule.max_date = rules.pop('max_date')

        rule.filters = rules
        rule.save()

        return redirect('admin:view_settings',
                        project_id=project_id, view_id=view_id)


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class ViewUpdate(APIView):
    """
    API Endpoints for a view in the AJAX API.
    /ajax/projects/:project_id/views/:view_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, view_id, format=None):
        """
        Updates a view
        """
        view = View.objects.as_admin(request.user, project_id, view_id)
        serializer = ViewSerializer(
            view, data=request.DATA, partial=True,
            fields=('id', 'name', 'description', 'status', 'isprivate')
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, format=None):
        """
        Deletes a view
        """
        view = View.objects.as_admin(request.user, project_id, view_id)
        view.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllContributionsViewUpdate(APIView):
    """
    API Endpoints for the all contributions view in the AJAX API.
    /ajax/projects/:project_id/views/all-contributions/
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, format=None):
        project = Project.objects.as_admin(request.user, project_id)
        if (request.DATA.get('isprivate') is not None):
            project.all_contrib_isprivate = request.DATA.get('isprivate')
            project.save()

        response = {
            'id': 'all-contributions',
            'name': 'All contributions',
            'description': 'This map provides access to all contributions ever contributed to the project.',
            'status': 'active',
            'isprivate': project.all_contrib_isprivate
        }

        return Response(response, status=status.HTTP_200_OK)


class ViewAjaxObservations(APIView):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, format=None):
        """
        Returns all data in a view
        /ajax/projects/:project_id/views/:view_id/observations/
        """
        view = View.objects.get_single(request.user, project_id, view_id)
        serializer = ContributionSerializer(view.data, many=True)
        return Response(serializer.data)
