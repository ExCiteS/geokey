import json

from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
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
from .forms import ViewCreateForm, ViewGroupCreateForm
from .models import View, ViewGroup, Rule
from .serializers import (
    ViewSerializer, ViewGroupSerializer
)


# ############################################################################
#
# Administration views
#
# ############################################################################

class ViewAdminCreateView(LoginRequiredMixin, CreateView):
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
            ViewAdminCreateView, self).get_context_data(**kwargs)

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
        return super(ViewAdminCreateView, self).form_valid(form)


class ViewAdminSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'views/view_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        view = View.objects.as_admin(user, project_id, view_id)
        return {'view': view, 'status_types': STATUS}


class ViewAdminDataView(LoginRequiredMixin, TemplateView):
    template_name = 'views/view_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        view = View.objects.get_single(user, project_id, view_id)
        project_views = View.objects.get_list(user, project_id)
        return {
            'view': view,
            'admin': view.project.is_admin(user),
            'project_views': project_views
        }


class ViewSingleObservation(LoginRequiredMixin, TemplateView):
    template_name = 'views/observation.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id, observation_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        view = View.objects.get_single(user, project_id, view_id)
        # check if the observation can be access through that view
        observation = Project.objects.get(pk=project_id).observations.get(
            pk=observation_id)

        return {
            'view': view,
            'observation': observation
        }


class ViewGroupAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create usergroup page
    """
    form_class = ViewGroupCreateForm
    template_name = 'views/view_group_create.html'

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']
        group_id = self.object.id
        return reverse(
            'admin:view_group_settings',
            kwargs={
                'project_id': project_id,
                'view_id': view_id,
                'group_id': group_id
            }
        )

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']

        context = super(
            ViewGroupAdminCreateView, self).get_context_data(**kwargs)

        context['view'] = View.objects.as_admin(
            self.request.user, project_id, view_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the view group.
        """
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']

        view = View.objects.as_admin(self.request.user, project_id, view_id)
        form.instance.view = view

        return super(ViewGroupAdminCreateView, self).form_valid(form)


class ViewGroupAdminSettingsView(LoginRequiredMixin, TemplateView):
    """
    Displays the usergroup admin page
    """
    template_name = 'views/view_group_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id, group_id, **kwargs):
        """
        Creates the request context for rendering the page
        """

        context = super(
            ViewGroupAdminSettingsView, self).get_context_data(**kwargs)

        context['group'] = ViewGroup.objects.as_admin(
            self.request.user, project_id, view_id, group_id
        )
        return context


class RuleCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the rule create page
    """
    template_name = 'views/view_rule_create.html'
    model = Rule

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']

        context = super(
            RuleCreateView, self).get_context_data(**kwargs)

        context['view'] = View.objects.as_admin(
            self.request.user, project_id, view_id
        )
        return context

    @handle_exceptions_for_admin
    def post(self, request, project_id, view_id):
        view = View.objects.as_admin(self.request.user, project_id, view_id)
        observation_type = ObservationType.objects.as_admin(
            self.request.user, project_id, request.POST.get('observationtype'))

        Rule.objects.create(
            view=view,
            observation_type=observation_type,
            filters=json.loads(request.POST.get('rules'))
        )

        return redirect('admin:view_settings',
                        project_id=project_id, view_id=view_id)


class RuleSettingsView(LoginRequiredMixin, TemplateView):
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
        context = super(RuleSettingsView, self).get_context_data(**kwargs)

        context['rule'] = view.rules.get(pk=rule_id)
        return context


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class ViewApiDetail(APIView):
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
        serializer = ViewSerializer(view, data=request.DATA, partial=True)

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


class ViewUserGroupApiDetail(APIView):
    """
    API Endpoints for a view in the AJAX API.
    /ajax/projects/:project_id/views/:view_id/usergroups/:group_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, view_id, group_id, format=None):
        """
        Updates a view
        """
        group = ViewGroup.objects.as_admin(
            request.user, project_id, view_id, group_id)
        serializer = ViewGroupSerializer(
            group, data=request.DATA, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, group_id, format=None):
        """
        Deletes a view
        """
        group = ViewGroup.objects.as_admin(
            request.user, project_id, view_id, group_id)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ViewUserGroupUsersApi(APIView):
    """
    API Endpoints for a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/views/:view_id/usergroups/:usergroup_id/users
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, view_id, group_id, format=None):
        """
        Adds a user to the usergroup
        """
        group = ViewGroup.objects.as_admin(
            request.user, project_id, view_id, group_id)

        try:
            user = User.objects.get(pk=request.DATA.get('userId'))
            group.users.add(user)

            serializer = ViewGroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                'The user you are trying to add to the user group does ' +
                'not exist',
                status=status.HTTP_400_BAD_REQUEST
            )


class ViewUserGroupUsersApiDetail(APIView):
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, group_id, user_id,
               format=None):
        """
        Removes a user from the user group
        """
        group = ViewGroup.objects.as_admin(
            request.user, project_id, view_id, group_id)

        user = group.users.get(pk=user_id)
        group.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ViewApiData(APIView):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, format=None):
        """
        Returns all data in a view
        /ajax/projects/:project_id/views/:view_id/data
        """
        view = View.objects.get_single(request.user, project_id, view_id)
        serializer = ContributionSerializer(view.data, many=True)
        return Response(serializer.data)


# ############################################################################
#
# Public API views
#
# ############################################################################

class SingleView(APIView):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, format=None):
        """
        Returns a single view and its data
        /api/projects/:project_id/views/:view_id/
        """
        view = View.objects.get_single(request.user, project_id, view_id)
        serializer = ViewSerializer(view)
        return Response(serializer.data)
