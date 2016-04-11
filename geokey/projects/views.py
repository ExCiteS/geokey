"""Views for projects."""

from django.db import IntegrityError
from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from geokey.core.decorators import (
    handle_exceptions_for_ajax,
    handle_exceptions_for_admin
)

from geokey.users.serializers import UserSerializer
from geokey.users.models import User
from geokey.categories.models import Category
from geokey.contributions.models import Comment, MediaFile

from .base import STATUS
from .models import Project, Admins
from .forms import ProjectCreateForm
from .serializers import ProjectSerializer


class ProjectContext(object):

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, *args, **kwargs):
        """
        Returns the context containing the project instance.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database

        Returns
        -------
        dict
            Context
        """

        project = Project.objects.as_admin(self.request.user, project_id)

        return super(ProjectContext, self).get_context_data(
            project=project,
            *args,
            **kwargs
        )


# ############################################################################
#
# Administration views
#
# ############################################################################

class ProjectCreate(LoginRequiredMixin, CreateView):

    """
    Displays the create project page.
    """
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def form_valid(self, form):
        """
        Creates the project and redirects to the project overview page.

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
            False,  # Project is never locked when creating it
            data.get('everyone_contributes'),
            self.request.user
        )

        add_another_url = reverse(
            'admin:project_create'
        )

        messages.success(
            self.request,
            mark_safe('The project has been created. <a href="%s">Add '
                      'another project.</a>' % add_another_url)
        )

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
            Context
        """

        projects = Project.objects.get_list(self.request.user).exclude(
            admins=self.request.user)
        projects_list = []

        for project in projects:
            projects_list.append({
                'name': project.name,
                'role': project.get_role(self.request.user),
                'contributions': project.observations.filter(
                    creator=self.request.user).count(),
            })

        return {'projects': projects_list}


class ProjectOverview(LoginRequiredMixin, ProjectContext, TemplateView):
    """Project overview page."""

    template_name = 'projects/project_overview.html'

    def get_context_data(self, project_id):
        """
        Return the context to render the view.

        Overwrite the method to add the project, number of contributions,
        comments and media files in total.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        dict
            Context
        """
        context = super(ProjectOverview, self).get_context_data(project_id)
        project = context.get('project')

        if project:
            contributions = project.observations.all()
            project.contributions_count = len(contributions)
            project.comments_count = Comment.objects.filter(
                commentto=contributions).count()
            project.media_count = MediaFile.objects.filter(
                contribution=contributions).count()

        return context


class ProjectGeographicExtent(LoginRequiredMixin, ProjectContext,
                              TemplateView):

    """
    Displays the page to edit the geograhic extent of the project.
    """
    template_name = 'projects/project_geographic_extent.html'

    def post(self, request, project_id):
        """
        Adds or updates the geographic extent of the project.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """

        data = request.POST
        context = self.get_context_data(project_id)
        project = context.get('project', None)
        geometry = data.get('geometry')

        if project is not None:
            if not project.islocked:
                if geometry is not None and len(geometry) > 0:
                    project.geographic_extent = GEOSGeometry(geometry)
                else:
                    project.geographic_extent = None

                project.save()
                context['project'] = project

                messages.success(
                    self.request,
                    'The geographic extent has been updated.'
                )
            else:
                messages.error(
                    self.request,
                    'The project is locked. Its structure cannot be edited.'
                )

        return self.render_to_response(context)


class ProjectSettings(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Displays the project settings page.
    """
    model = Project
    template_name = 'projects/project_settings.html'

    def get_context_data(self, project_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the project and status types to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database

        Returns
        -------
        dict
            Context
        """

        return super(ProjectSettings, self).get_context_data(
            project_id,
            status_types=STATUS
        )

    def post(self, request, project_id):
        """
        Updates the project settings.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """

        context = self.get_context_data(project_id)
        project = context.get('project', None)

        if project is not None:
            data = request.POST

            project.name = strip_tags(data.get('name'))
            project.description = strip_tags(data.get('description'))
            project.everyone_contributes = data.get('everyone_contributes')
            project.save()
            context['project'] = project

            messages.success(self.request, 'The project has been updated.')

        return self.render_to_response(context)


class ProjectDelete(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Deletes the project.
    """
    template_name = 'base.html'

    def get(self, request, project_id):
        """
        Deletes the project.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirecting to the dashboard
        django.http.HttpResponse
            If user is not administrator of the project, the error message is
            rendered
        """

        context = self.get_context_data(project_id)
        project = context.get('project', None)

        if project is not None:
            if not project.islocked:
                project.delete()
                messages.success(self.request, 'The project has been deleted.')
                return redirect('admin:dashboard')
            else:
                messages.error(
                    self.request,
                    'The project is locked. It cannot be deleted.'
                )
                return redirect(
                    'admin:project_settings', project_id=project.id)

        return redirect('admin:dashboard')


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
        rest_framework.response.Response
            Response containing the serialised project or an error message
        """

        project = Project.objects.as_admin(request.user, project_id)

        serializer = ProjectSerializer(
            project, data=request.data, partial=True,
            fields=(
                'id', 'name', 'description', 'status', 'isprivate', 'islocked',
                'everyone_contributes'
            )
        )

        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data['everyone_contributes'] = project.everyone_contributes
            return Response(data)

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
        rest_framework.response.Response
            Response containing the serialised list of admins or an error
            message.
        """

        project = Project.objects.as_admin(request.user, project_id)
        user = User.objects.get(pk=request.data.get('user_id'))

        try:
            Admins.objects.create(project=project, user=user)
        except IntegrityError:
            return Response(
                'The user is already an administrator of this project.',
                status=status.HTTP_400_BAD_REQUEST
            )

        refreshed_admins = Project.objects.get(pk=project_id).admins.all()
        serializer = UserSerializer(refreshed_admins, many=True)

        return Response(
            {'users': serializer.data},
            status=status.HTTP_201_CREATED
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
        rest_framework.response.Response
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
        rest_framework.response.Response
            Contains the serialised project or an error message
        """

        project = Project.objects.as_admin(request.user, project_id)

        try:
            project.reorder_categories(request.data.get('order'))

            serializer = ProjectSerializer(
                project,
                fields=(
                    'id', 'name', 'description', 'status', 'isprivate',
                    'islocked', 'everyone_contributes'
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
# PUBLIC API
#
# ############################################################################

class Projects(APIView):
    """Public API for all projects."""

    @handle_exceptions_for_ajax
    def get(self, request):
        """
        Handle GET request.

        Return a list a all projects accessible to the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.response.Response
            Contains serialized list of projects.
        """
        user = request.user
        projects = Project.objects.get_list(user).filter(status='active')
        serializer = ProjectSerializer(
            projects,
            many=True,
            context={'user': user},
            fields=('id', 'name', 'description', 'user_info')
        )
        return Response(serializer.data)


class SingleProject(APIView):
    """Public API for a single project."""

    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Handle GET request.

        Return a single project.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        rest_framework.response.Response
            Contains the serialized project.

        Raises
        ------
        PermissionDenied
            When the project is inactive (handled in the
            handle_exceptions_for_ajax decorator).
        """
        user = request.user
        project = Project.objects.get_single(user, project_id)

        if project.status == 'active':
            serializer = ProjectSerializer(
                project,
                context={'user': user}
            )
            return Response(serializer.data)

        raise PermissionDenied('The project is inactive and therefore '
                               'not accessable through the public API.')
