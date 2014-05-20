from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from dataviews.models import View
from contributions.serializers import ContributionSerializer
from users.serializers import UserSerializer

from .base import STATUS
from .models import Project
from .forms import ProjectCreateForm
from .serializers import ProjectSerializer


# ############################################################################
#
# Administration views
#
# ############################################################################

class ProjectCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create project page
    """
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def form_valid(self, form):
        """
        Creates the project and redirects to the project overview page
        """
        data = form.cleaned_data
        project = Project.create(
            data.get('name'),
            data.get('description'),
            data.get('isprivate'),
            self.request.user
        )
        return redirect('admin:project_settings', project_id=project.id)


class ProjectSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the project settings page
    """
    model = Project
    template_name = 'projects/project_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return {
            'project': project,
            'status_types': STATUS
        }

    def dispatch(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        print project_id
        project = Project.objects.get_single(request.user, project_id)

        if project.is_admin(request.user):
            return super(ProjectSettings, self).dispatch(
                request, *args, **kwargs)
        elif project.can_contribute(request.user):
            return redirect(reverse('admin:project_my_observations', kwargs={
                'project_id': project_id,
            }))
        else:
            views = View.objects.get_list(request.user, project_id)
            return redirect(reverse('admin:view_observations', kwargs={
                'project_id': project_id,
                'view_id': views[0].id
            }))


class ProjectObservations(LoginRequiredMixin, TemplateView):
    """
    Displays the project overview page
    """
    model = Project
    template_name = 'contributions/observations.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        project = Project.objects.get_single(user, project_id)
        views = View.objects.get_list(user, project_id)
        return {
            'project': project,
            'views': views,
            'admin': project.is_admin(user),
            'contributor': project.can_contribute(user),
        }


class ProjectMyObservations(LoginRequiredMixin, TemplateView):
    model = Project
    template_name = 'contributions/observations.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        project = Project.objects.get_single(user, project_id)
        views = View.objects.get_list(user, project_id)
        return {
            'project': project,
            'views': views,
            'admin': project.is_admin(user),
            'contributor': project.can_contribute(user),
            'my_contributions': True
        }


class ProjectSingleObservation(LoginRequiredMixin, TemplateView):
    template_name = 'contributions/observation.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, observation_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        project = Project.objects.as_admin(user, project_id)
        observation = project.observations.get(
            pk=observation_id)

        return {
            'project': project,
            'observation': observation
        }


class ProjectSingleMyObservation(LoginRequiredMixin, TemplateView):
    template_name = 'contributions/observation.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, observation_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        project = Project.objects.as_contributor(user, project_id)
        observation = project.observations.filter(creator=user).get(
            pk=observation_id)

        return {
            'project': project,
            'observation': observation
        }


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class ProjectUpdate(APIView):
    """
    API Endpoint for a project in the AJAX API.
    /ajax/projects/:project_id
    """

    @handle_exceptions_for_ajax
    def put(self, request, project_id, format=None):
        """
        Updates a project
        """
        project = Project.objects.as_admin(request.user, project_id)
        serializer = ProjectSerializer(
            project, data=request.DATA, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, format=None):
        """
        Deletes a project
        """
        project = Project.objects.as_admin(request.user, project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectAdmins(APIView):
    @handle_exceptions_for_ajax
    def post(self, request, project_id, format=None):
        """
        Adds a user to the usergroup
        """
        project = Project.objects.as_admin(request.user, project_id)

        try:
            user = User.objects.get(pk=request.DATA.get('userId'))
            project.admins.add(user)

            serializer = UserSerializer(project.admins.all(), many=True)
            return Response(
                {'users': serializer.data}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                'The user you are trying to add to the user group does ' +
                'not exist',
                status=status.HTTP_400_BAD_REQUEST
            )


class ProjectAdminsUser(APIView):
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, user_id, format=None):
        """
        Removes a user from the user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        user = project.admins.get(pk=user_id)
        project.admins.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectAjaxObservations(APIView):
    """
    API Endpoint for a project in the AJAX API.
    /ajax/projects/:project_id/observations/
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        project = Project.objects.as_admin(request.user, project_id)
        serializer = ContributionSerializer(
            project.observations.all(), many=True)
        return Response(serializer.data)


class ProjectAjaxMyObservations(APIView):
    """
    API Endpoint for a project in the AJAX API.
    /ajax/projects/:project_id/mycontributions/
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        project = Project.objects.as_contributor(request.user, project_id)
        serializer = ContributionSerializer(
            project.observations.filter(creator=request.user), many=True)
        return Response(serializer.data)


# ############################################################################
#
# Public API views
#
# ############################################################################

class Projects(APIView):
    """
    API Endpoint for project list in the public API.
    /api/projects
    """
    @handle_exceptions_for_ajax
    def get(self, request, format=None):
        """
        Returns a list a all projects accessable to the user
        """
        projects = Project.objects.get_list(
            request.user).filter(status='active')
        serializer = ProjectSerializer(
            projects, many=True,
            fields=('id', 'name', 'description', 'status')
        )
        return Response(serializer.data)


class SingleProject(APIView):
    """
    API Endpoint for single project in the public API.
    /api/projects
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        """
        Returns a list a all projects accessable to the user
        """
        project = Project.objects.get_single(request.user, project_id)
        if project.status == 'active':
            serializer = ProjectSerializer(
                project, context={'request': request}
            )
            return Response(serializer.data)
        else:
            raise PermissionDenied('The project is inactive and therefore '
                                   'not accessable through the public API.')
