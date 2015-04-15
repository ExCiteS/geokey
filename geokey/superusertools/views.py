from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

from braces.views import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework import status

from geokey.projects.models import Project
from geokey.users.models import User
from geokey.users.serializers import UserSerializer


# #############################################################################
#
# ADMIN VIEWS
#
# #############################################################################


class SuperuserMixin(object):
    """
    Mixin to check if the user is a super user
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request. Either responds with an Error message or calls
        View's dispatch method.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.

        Returns
        -------
        django.http.HttpResponse

        """
        if not request.user.is_superuser:
            return self.render_to_response({
                'error_description': 'Superuser tools are for superusers only.'
                                     ' You are not a superuser.',
                'error': 'Permission denied.'
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)


class PlatformSettings(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """
    Change the settings of the platform
    """
    template_name = 'superusertools/platform_settings.html'

    def get_context_data(self):
        """
        Returns the context to render the view, adds current site to context

        Returns
        -------
        dict
        """
        return {'site': get_current_site(self.request)}

    def post(self, request):
        """
        Updates the platform settings

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.

        Returns
        -------
        django.http.HttpResponse
        """
        data = request.POST
        context = self.get_context_data()
        site = context.pop('site', None)

        if site is not None:
            site.name = data.get('name')
            site.domain = data.get('domain')
            site.save()
            messages.success(
                self.request,
                "The platform settings have been updated."
            )

        context['site'] = site
        return self.render_to_response(context)


class ProjectsList(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """
    Displays a list of all projects
    """
    template_name = 'superusertools/projects_list.html'

    def get_context_data(self):
        """
        Returns the context to render the view, adds list of projects to
        context

        Returns
        -------
        dict
        """
        return {'projects': Project.objects.all()}


class ManageSuperUsers(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """
    View to add and remove superusers
    """
    template_name = 'superusertools/manage_users.html'

    def get_context_data(self):
        """
        Returns the context to render the view, adds list of superusers to
        context

        Returns
        -------
        dict
        """
        return {'superusers': User.objects.filter(is_superuser=True)}


# #############################################################################
#
# ADMIN AJAX VIEWS
#
# #############################################################################


class IsSuperUser(BasePermission):
    """
    Checks whether the authenticated user is a superiser
    """
    def has_permission(self, request, view):
        """
        Returns True if the user is a superuser

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        view : rest_framework.views.APIView
            View that called the permission

        Return
        ------
        Boolean
            indicating if user is a super user
        """
        return request.user and request.user.is_superuser


class AddSuperUsersAjaxView(APIView):
    """
    AJAX API endpoint to add superusers
    """
    permission_classes = (IsSuperUser,)

    def post(self, request):
        """
        Adds a new superuser

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request

        Returns
        -------
        rest_framework.response.Response
            Contains the list of superusers or an error message
        """
        try:
            user = User.objects.get(pk=request.DATA.get('userId'))
            user.is_superuser = True
            user.save()

            superusers = User.objects.filter(is_superuser=True)
            serializer = UserSerializer(superusers, many=True)
            return Response(
                {'users': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                'The user you are trying to add to the user group does ' +
                'not exist',
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteSuperUsersAjaxView(APIView):
    """
    AJAX API endpoint to remove superusers
    """
    permission_classes = (IsSuperUser,)

    def delete(self, request, user_id):
        """
        Deletes a superuser

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request

        Returns
        -------
        rest_framework.response.Response
            Empty response indicating success an error message
        """
        try:
            user = User.objects.filter(is_superuser=True).get(pk=user_id)
            user.is_superuser = False
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response(
                'Superuser does not exist.',
                status=status.HTTP_404_NOT_FOUND
            )
