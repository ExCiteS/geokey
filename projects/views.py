from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.html import strip_tags
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from core.exceptions import Unauthenticated
from users.serializers import UserSerializer
from users.models import User

from .base import STATUS
from .models import Project, Admins
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
    `/admin/projects/new`
    """
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def form_valid(self, form):
        """
        Creates the project and redirects to the project overview page
        """
        data = form.cleaned_data
        project = Project.create(
            strip_tags(data.get('name')),
            strip_tags(data.get('description')),
            data.get('isprivate'),
            data.get('everyone_contributes'),
            self.request.user
        )
        messages.success(self.request, "The project has been created.")
        return redirect('admin:project_overview', project_id=project.id)


class ProjectsInvolved(LoginRequiredMixin, TemplateView):
    template_name = 'projects/projects_involved.html'

    def get_context_data(self):
        projects = Project.objects.get_list(self.request.user).exclude(
            admins=self.request.user)
        project_list = []

        for project in projects:
            project_list.append({
                'name': project.name,
                'role': project.get_role(self.request.user),
                'contributions': project.observations.filter(
                    creator=self.request.user).count(),
            })

        return {
            'projects': project_list
        }


class ProjectOverview(LoginRequiredMixin, TemplateView):
    """
    Displays the project overview page
    `/admin/projects/:project_id`
    """
    model = Project
    template_name = 'projects/project_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page. If the user is not
        an administrator of the project, `PermissionDenied` is caught and
        handled in the `handle_exceptions_for_admin` decorator and an error
        message is displayed.
        """
        user = self.request.user
        project = Project.objects.as_admin(user, project_id)
        contributions = project.observations.all()

        return {
            'project': project,
            'allcontributions': contributions.count(),
            'contributions': contributions.filter(
                creator=self.request.user).count()
        }


class ProjectExtend(LoginRequiredMixin, TemplateView):
    template_name = 'projects/project_extend.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page. If the user is not
        an administrator of the project, `PermissionDenied` is caught and
        handled in the `handle_exceptions_for_admin` decorator and an error
        message is displayed.
        """
        project = Project.objects.as_admin(self.request.user, project_id)

        context = super(ProjectExtend, self).get_context_data()
        context['project'] = project

        return context

    def post(self, request, project_id):
        data = request.POST
        context = self.get_context_data(project_id)
        project = context.pop('project', None)
        geometry = data.get('geometry')

        if project is not None:
            if geometry is not None and len(geometry) > 0:
                project.geographic_extend = GEOSGeometry(data.get('geometry'))
            else:
                project.geographic_extend = None

            project.save()

            messages.success(
                self.request,
                'The geographic extend has been updated successfully.'
            )

            context['project'] = project
            return self.render_to_response(context)


class ProjectSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the project settings page
    `/admin/projects/:project_id/settings/`
    """
    model = Project
    template_name = 'projects/project_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page. If the user is not
        an administrator of the project, `PermissionDenied` is caught and
        handled in the `handle_exceptions_for_admin` decorator and an error
        message is displayed.
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return {
            'project': project,
            'status_types': STATUS
        }

    def post(self, request, project_id):
        context = self.get_context_data(project_id)
        project = context.pop('project')
        data = request.POST

        project.name = strip_tags(data.get('name'))
        project.description = strip_tags(data.get('description'))
        project.everyone_contributes = data.get('everyone_contributes')
        project.save()

        messages.success(self.request, "The project has been updated.")
        context['project'] = project
        return self.render_to_response(context)


class ProjectDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, **kwargs):
        project = Project.objects.as_admin(self.request.user, project_id)
        return super(ProjectDelete, self).get_context_data(
            project=project, **kwargs)

    def get(self, request, project_id):
        context = self.get_context_data(project_id)
        project = context.pop('project', None)

        if project is not None:
            project.delete()

            messages.success(self.request, "The project has been deleted.")
            return redirect('admin:dashboard')

        return self.render_to_response(context)


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class ProjectUpdate(APIView):
    """
    AJAX Endpoint for a project update.
    /ajax/projects/:project_id
    """

    @handle_exceptions_for_ajax
    def put(self, request, project_id, format=None):
        """
        Updates a project. If the user is not an administrator of the project,
        `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_ajax` decorator and an error 403 is returned.
        """
        project = Project.objects.as_admin(request.user, project_id)
        serializer = ProjectSerializer(
            project, data=request.DATA, partial=True,
            fields=(
                'id', 'name', 'description', 'status', 'isprivate',
                'everyone_contributes'
            )
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, format=None):
        """
        Deletes a project. If the user is not an administrator of the project,
        `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_ajax` decorator and an error 403 is returned.
        """
        project = Project.objects.as_admin(request.user, project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectAdmins(APIView):
    """
    AJAX Endpoint for project administrators.
    /ajax/projects/:project_id/admins
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, format=None):
        """
        Adds a user to the admin group. . If the user is not an administrator
        of the project, `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_ajax` decorator and an error 403 is returned.
        """
        project = Project.objects.as_admin(request.user, project_id)

        try:
            user = User.objects.get(pk=request.DATA.get('userId'))
            Admins.objects.create(project=project, user=user)

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
    """
    AJAX Endpoint for a single project administrator.
    /ajax/projects/:project_id/admins
    """

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, user_id, format=None):
        """
        Removes a user from the user group. . If the user is not an
        administrator of the project, `PermissionDenied` is caught and handled
        in the `handle_exceptions_for_ajax` decorator and an error 403 is
        returned.
        """
        project = Project.objects.as_admin(request.user, project_id)
        user = project.admins.get(pk=user_id)
        Admins.objects.get(project=project, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ############################################################################
#
# Public API views
#
# ############################################################################

class Projects(APIView):
    """
    API Endpoint for project list in the public API.
    /api/projects/
    """
    @handle_exceptions_for_ajax
    def get(self, request, format=None):
        """
        Returns a list a all projects accessable to the user.
        """
        projects = Project.objects.get_list(
            request.user).filter(status='active')
        serializer = ProjectSerializer(
            projects, many=True, context={'user': request.user},
            fields=('id', 'name', 'description', 'user_info')
        )
        return Response(serializer.data)


class SingleProject(APIView):
    """
    API Endpoint for single project in the public API.
    /api/projects/:project_id/
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        """
        Returns a single project. If the user is not eligable to access the
        project, `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_ajax` decorator and an error 403 is returned.
        """
        project = Project.objects.get_single(request.user, project_id)
        if project.status == 'active':
            serializer = ProjectSerializer(
                project, context={'user': request.user}
            )
            return Response(serializer.data)

        raise PermissionDenied('The project is inactive and therefore '
                               'not accessable through the public API.')


class ProjectContactAdmins(APIView):
    """
    API Endpoint for single project in the public API.
    /api/projects/:project_id/get-in-touch/
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, format=None):
        """
        Sends an email to all admins that are contact persons for the given
        project.
        """
        user = request.user
        if user.is_anonymous():
            raise Unauthenticated('Unauthenticated users can not contact the '
                                  'administrators of the project.')

        email_text = self.request.DATA.get('email_text')
        project = Project.objects.get_single(request.user, project_id)
        if project.status == 'active':
            project.contact_admins(user, email_text)
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied('The project is inactive and therefore '
                               'not accessable through the public API.')
