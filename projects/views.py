from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from dataviews.models import View

from .base import STATUS
from .models import Project, UserGroup
from .forms import ProjectCreateForm
from .serializers import ProjectSerializer, UserGroupSerializer


# ############################################################################
#
# Administration views
#
# ############################################################################

class ProjectAdminCreateView(LoginRequiredMixin, CreateView):
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


class ProjectAdminDetailView(LoginRequiredMixin, TemplateView):
    """
    Displays the project overview page
    """
    model = Project
    template_name = 'projects/project_view.html'

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
            'admin': project.is_admin(user)
        }


class ProjectAdminSettings(LoginRequiredMixin, TemplateView):
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


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class ProjectApiDetail(APIView):
    """
    API Endpoints for a project in the AJAX API.
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


class ProjectApiUserGroup(APIView):
    """
    API Endpoints for a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id, format=None):
        """
        Adds a user to the usergroup
        """
        project = Project.objects.as_admin(request.user, project_id)

        if project.admins.id == int(group_id):
            group = project.admins
        elif project.contributors.id == int(group_id):
            group = project.contributors
        else:
            raise UserGroup.DoesNotExist

        try:
            user = User.objects.get(pk=request.DATA.get('userId'))
            group.users.add(user)

            serializer = UserGroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                'The user you are trying to add to the user group does ' +
                'not exist',
                status=status.HTTP_400_BAD_REQUEST
            )


class ProjectApiUserGroupUser(APIView):
    """
    API Endpoints for a user in a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users/:user_id
    """

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, user_id, format=None):
        """
        Removes a user from the user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        if project.admins.id == int(group_id):
            group = project.admins
        elif project.contributors.id == int(group_id):
            group = project.contributors
        else:
            raise UserGroup.DoesNotExist

        user = group.users.get(pk=user_id)
        group.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ############################################################################
#
# Public API views
#
# ############################################################################

class ProjectApiList(APIView):
    """
    API Endpoints projects in the public API.
    /api/projects
    """
    @handle_exceptions_for_ajax
    def get(self, request, format=None):
        """
        Returns a list a all projects accessable to the user
        """
        projects = Project.objects.get_list(request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
