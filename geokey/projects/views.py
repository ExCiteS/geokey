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

from geokey.core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from geokey.core.exceptions import Unauthenticated
from geokey.users.serializers import UserSerializer
from geokey.users.models import User
from geokey.categories.models import Category

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

        Parameters
        ----------
        form : geokey.projects.forms.ProjectCreateForm
            Represents the user input
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
    """
    Displays a list of all projects the user is involved in
    """
    template_name = 'projects/projects_involved.html'

    def get_context_data(self):
        """
        Returns the context to render the view. Overwrites the method to add
        the list of projects to the context.

        Returns
        -------
        dict
            context
        """
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
        Returns the context to render the view. Overwrites the method to add
        the project, number of contributions and number of user contributions
        to the context.

        Parameters
        ----------
        project_id : int
            identifies the project in the database

        Returns
        -------
        dict
            context
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
    """
    Displays the page to edit the geograhic extent of the project
    """
    template_name = 'projects/project_extend.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the project to the context.

        Parameters
        ----------
        project_id : int
            identifies the project in the database

        Returns
        -------
        dict
            context
        """
        project = Project.objects.as_admin(self.request.user, project_id)

        context = super(ProjectExtend, self).get_context_data()
        context['project'] = project

        return context

    def post(self, request, project_id):
        """
        Adds or updates the geographic extent of the project.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
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
                'The geographic extent has been updated successfully.'
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
        Returns the context to render the view. Overwrites the method to add
        the project and status types to the context.

        Parameters
        ----------
        project_id : int
            identifies the project in the database

        Returns
        -------
        dict
            context
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return {
            'project': project,
            'status_types': STATUS
        }

    def post(self, request, project_id):
        """
        Updates the project settings

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id)
        project = context.pop('project')

        if project is not None:
            data = request.POST

            project.name = strip_tags(data.get('name'))
            project.description = strip_tags(data.get('description'))
            project.everyone_contributes = data.get('everyone_contributes')
            project.save()

            messages.success(self.request, "The project has been updated.")
            context['project'] = project
        return self.render_to_response(context)


class ProjectDelete(LoginRequiredMixin, TemplateView):
    """
    Deletes a project
    """
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the project and status types to the context.

        Parameters
        ----------
        project_id : int
            identifies the project in the database

        Returns
        -------
        dict
            context
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return super(ProjectDelete, self).get_context_data(
            project=project, **kwargs)

    def get(self, request, project_id):
        """
        Deletes the project

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            redirecting to the dashboard

        django.http.HttpResponse
            If user is not administrator of the project, the error message is
            rendered.
        """
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
    def put(self, request, project_id):
        """
        Updates a project.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        rest_framework.reponse.Response
            Response containing the serialised project or an error message
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


class ProjectAdmins(APIView):
    """
    AJAX Endpoint for project administrators.
    /ajax/projects/:project_id/admins
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id):
        """
        Adds a user to the admin group.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        rest_framework.reponse.Response
            Response containing the serialised list of admins or an error
            message.
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
    def delete(self, request, project_id, user_id):
        """
        Removes a user from the user group.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        rest_framework.reponse.Response
            Empty response if successful or response containing an error
            message.
        """
        project = Project.objects.as_admin(request.user, project_id)
        user = project.admins.get(pk=user_id)
        Admins.objects.get(project=project, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoriesReorderView(APIView):
    """
    AJAX Endpoint to re-order categories in a project.
    /ajax/projects/:project_id/cotegories/re-order
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id):
        """
        Reorders the cateories in the project.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        rest_framework.reponse.Response
            Contains the serialised project or an error message
        """
        project = Project.objects.as_admin(request.user, project_id)

        try:
            project.re_order_categories(request.DATA.get('order'))

            serializer = ProjectSerializer(
                project,
                fields=(
                    'id', 'name', 'description', 'status', 'isprivate',
                    'everyone_contributes'
                )
            )
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(
                {'error': 'One or more categories ids where not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )


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
    def get(self, request):
        """
        Returns a list a all projects accessible to the user.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.reponse.Response
            Contains serialised list of projects
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
    def get(self, request, project_id):
        """
        Returns a single project.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        rest_framework.reponse.Response
            Contains the serialised project

        Raises
        ------
        PermissionDenied
            if the project is inactive, is handled in the
            handle_exceptions_for_ajax decorator
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
    def post(self, request, project_id):
        """
        Sends an email to all admins that are contact persons for the given
        project.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            identifies the project in the database

        Returns
        -------
        rest_framework.reponse.Response
            Empty reponse indicating success

        Raises
        ------
        Unauthenticated
            if the user is anonymous; is handled in the
            handle_exceptions_for_ajax decorator
        """
        user = request.user
        if user.is_anonymous():
            raise Unauthenticated('Unauthenticated users can not contact the '
                                  'administrators of the project.')

        email_text = self.request.DATA.get('email_text')
        project = Project.objects.get_single(request.user, project_id)

        project.contact_admins(user, email_text)
        return Response(status=status.HTTP_204_NO_CONTENT)
