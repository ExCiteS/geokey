import json

from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages

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

class GroupingList(LoginRequiredMixin, TemplateView):
    template_name = 'views/grouping_list.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user

        context = super(GroupingList, self).get_context_data()
        context['project'] = Project.objects.as_admin(user, project_id)

        return context

class ViewCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create view page
    """
    form_class = ViewCreateForm
    template_name = 'views/view_create.html'

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:grouping_overview',
            kwargs={'project_id': project_id, 'grouping_id': self.object.id}
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
        messages.success(self.request, "The data grouping has been created.")
        return super(ViewCreate, self).form_valid(form)


class GroupingOverview(LoginRequiredMixin, TemplateView):
    template_name = 'views/grouping_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = View.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingOverview, self).get_context_data(grouping=grouping)


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

    def post(self, request, project_id, view_id):
        context = self.get_context_data(project_id, view_id)
        grouping = context.pop('view')
        data = request.POST

        grouping.name = data.get('name')
        grouping.description = data.get('description')
        grouping.save()

        messages.success(self.request, "The data grouping has been updated.")
        context['view'] = grouping
        return self.render_to_response(context)


class GroupingPermissions(LoginRequiredMixin, TemplateView):
    template_name = 'views/grouping_permissions.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = View.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingPermissions, self).get_context_data(grouping=grouping)


class GroupingDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = View.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingDelete, self).get_context_data(grouping=grouping)
    
    def get(self, request, project_id, grouping_id):
        context = self.get_context_data(project_id, grouping_id)
        grouping = context.pop('grouping', None)

        if grouping is not None:
            grouping.delete()

        messages.success(self.request, 'The data grouping has been deleted')

        return redirect('admin:grouping_list', project_id=project_id)


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

        context['grouping'] = View.objects.as_admin(
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
        messages.success(self.request, 'The filter has been created.')
        return redirect('admin:grouping_overview',
                        project_id=project_id, grouping_id=view_id)


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

        rules = None
        min_date = None
        max_date = None

        try:
            rules = json.loads(request.POST.get('rules'))
            rule.min_date = rules.pop('min_date')
            rule.max_date = rules.pop('max_date')
        except ValueError:
            pass

        rule.filters = rules
        rule.save()
        messages.success(self.request, 'The filter has been updated.')
        return redirect('admin:grouping_overview',
                        project_id=project_id, grouping_id=view_id)


class FilterDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id, filter_id, **kwargs):
        """
        Creates the request context for rendering the page
        """
        grouping = View.objects.as_admin(
            self.request.user, project_id, grouping_id)
        context = super(FilterDelete, self).get_context_data(**kwargs)

        context['filter'] = grouping.rules.get(pk=filter_id)
        return context

    def get(self, request, project_id, grouping_id, filter_id):
        context = self.get_context_data(project_id, grouping_id, filter_id)
        data_filter = context.pop('filter', None)

        if data_filter is not None:
            data_filter.delete()

        messages.success(self.request, 'The filter has been deleted')

        return redirect('admin:grouping_overview',
                        project_id=project_id, grouping_id=grouping_id)


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
