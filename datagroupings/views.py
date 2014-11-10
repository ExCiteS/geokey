import json

from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import strip_tags

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project
from categories.models import Category

from .base import STATUS
from .forms import GroupingCreateForm
from .models import Grouping, Rule
from .serializers import GroupingSerializer


# ############################################################################
#
# Administration views
#
# ############################################################################

class GroupingList(LoginRequiredMixin, TemplateView):
    template_name = 'datagroupings/grouping_list.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user

        context = super(GroupingList, self).get_context_data()
        context['project'] = Project.objects.as_admin(user, project_id)

        return context


class GroupingCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create view page
    """
    form_class = GroupingCreateForm
    template_name = 'datagroupings/grouping_create.html'

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
            GroupingCreate, self).get_context_data(**kwargs)

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
        return super(GroupingCreate, self).form_valid(form)


class GroupingOverview(LoginRequiredMixin, TemplateView):
    template_name = 'datagroupings/grouping_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingOverview, self).get_context_data(
            grouping=grouping
        )


class GroupingSettings(LoginRequiredMixin, TemplateView):
    template_name = 'datagroupings/grouping_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return {'grouping': grouping, 'status_types': STATUS}

    def post(self, request, project_id, grouping_id):
        context = self.get_context_data(project_id, grouping_id)
        grouping = context.pop('grouping')
        data = request.POST

        grouping.name = strip_tags(data.get('name'))
        grouping.description = strip_tags(data.get('description'))
        grouping.save()

        messages.success(self.request, "The data grouping has been updated.")
        context['grouping'] = grouping
        return self.render_to_response(context)


class GroupingPermissions(LoginRequiredMixin, TemplateView):
    template_name = 'datagroupings/grouping_permissions.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingPermissions, self).get_context_data(
            grouping=grouping
        )


class GroupingDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
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
    template_name = 'datagroupings/rule_create.html'
    model = Rule

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Returns the context data for creating the view.
        """
        project_id = self.kwargs['project_id']
        grouping_id = self.kwargs['grouping_id']

        context = super(
            RuleCreate, self).get_context_data(**kwargs)

        context['grouping'] = Grouping.objects.as_admin(
            self.request.user, project_id, grouping_id
        )
        return context

    @handle_exceptions_for_admin
    def post(self, request, project_id, grouping_id):
        """
        Creates a new Rule with the POSTed data.
        """
        grouping = Grouping.objects.as_admin(
            self.request.user,
            project_id,
            grouping_id
        )
        category = Category.objects.as_admin(
            self.request.user, project_id, request.POST.get('category'))

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
            grouping=grouping,
            category=category,
            min_date=min_date,
            max_date=max_date,
            filters=rules
        )
        messages.success(self.request, 'The filter has been created.')
        return redirect('admin:grouping_overview',
                        project_id=project_id, grouping_id=grouping_id)


class RuleSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the settings page
    """
    template_name = 'datagroupings/rule_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id, rule_id, **kwargs):
        """
        Creates the request context for rendering the page
        """
        view = Grouping.objects.as_admin(
            self.request.user,
            project_id,
            grouping_id
        )
        context = super(RuleSettings, self).get_context_data(**kwargs)

        context['rule'] = view.rules.get(pk=rule_id)
        return context

    @handle_exceptions_for_admin
    def post(self, request, project_id, grouping_id, rule_id):
        view = Grouping.objects.as_admin(
            self.request.user,
            project_id,
            grouping_id
        )
        rule = view.rules.get(pk=rule_id)

        rules = None

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
                        project_id=project_id, grouping_id=grouping_id)


class FilterDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id, filter_id, **kwargs):
        """
        Creates the request context for rendering the page
        """
        grouping = Grouping.objects.as_admin(
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

class GroupingUpdate(APIView):
    """
    API Endpoints for a view in the AJAX API.
    /ajax/projects/:project_id/views/:grouping_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, grouping_id, format=None):
        """
        Updates a view
        """
        view = Grouping.objects.as_admin(request.user, project_id, grouping_id)
        serializer = GroupingSerializer(
            view, data=request.DATA, partial=True,
            fields=('id', 'name', 'description', 'status', 'isprivate')
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
