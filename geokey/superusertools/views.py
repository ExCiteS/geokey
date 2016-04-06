"""All views for superusertools."""

from django.db.models import Q, Case, When, Sum, IntegerField
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from braces.views import LoginRequiredMixin
from allauth.account.models import EmailAddress

from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.users.models import User
from geokey.users.serializers import UserSerializer
from geokey.projects.models import Project
from geokey.contributions.base import OBSERVATION_STATUS


# #############################################################################
#
# MIXINS
#
# #############################################################################

class SuperuserMixin(object):
    """Mixin to check if user is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request.

        Responds either with an error message, or calls a dispatch method of a
        view.

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
                'error': 'Permission denied.',
                'error_description': 'No rights to access superuser tools.'
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)


# #############################################################################
#
# ADMIN VIEWS
#
# #############################################################################

class ManageSuperusers(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Manage superusers page."""

    template_name = 'superusertools/manage_superusers.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Adds a list of superusers to the context.

        Returns
        -------
        dict
        """
        return {
            'superusers': User.objects.filter(
                is_superuser=True).only('display_name')
        }


class ManageInactiveUsers(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Manage inactive users page."""

    template_name = 'superusertools/manage_inactive_users.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Add a list of inactive users to the context.

        Returns
        -------
        dict
        """
        return {'inactive_users': User.objects.filter(
            is_active=False).defer('is_superuser')}

    def post(self, request):
        """
        Activate inactive users.

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
        inactive_users = context.get('inactive_users')

        if inactive_users:
            active_users = inactive_users.filter(
                id__in=data.getlist('activate_users'))

            for email in EmailAddress.objects.filter(user__in=active_users):
                email.verified = True
                email.set_as_primary(conditional=True)
                email.save()

            active_users.update(is_active=True)
            messages.success(
                self.request,
                '%s users were activated.' % len(active_users)
            )
            context['inactive_users'] = User.objects.filter(is_active=False)

        return self.render_to_response(context)


class ManageProjects(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Manage projects page."""

    template_name = 'superusertools/manage_projects.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Add a list of projects to the context (with numbers in total for
        contributions, comments, media files).

        Returns
        -------
        dict
        """
        return {'projects': Project.objects.all().annotate(
            contributions_count=Sum(Case(When(
                ~Q(observations__status=OBSERVATION_STATUS.deleted) &
                Q(observations__isnull=False),
                then=1
            ), default=0, output_field=IntegerField()), distinct=True),
            comments_count=Sum(Case(When(
                ~Q(observations__status=OBSERVATION_STATUS.deleted) &
                Q(observations__isnull=False),
                then='observations__num_comments'
            ), default=0, output_field=IntegerField()), distinct=True),
            media_count=Sum(Case(When(
                ~Q(observations__status=OBSERVATION_STATUS.deleted) &
                Q(observations__isnull=False),
                then='observations__num_media'
            ), default=0, output_field=IntegerField()), distinct=True)
        )}


class PlatformSettings(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Platform settings page."""

    template_name = 'superusertools/platform_settings.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Add a current site to the context.

        Returns
        -------
        dict
        """
        return {'site': get_current_site(self.request)}

    def post(self, request):
        """
        Update the platform settings.

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
        site = context.get('site')

        if site:
            site.name = data.get('name')
            site.domain = data.get('domain')
            site.save()
            messages.success(
                self.request,
                'Platform settings have been updated.'
            )
            context['site'] = site

        return self.render_to_response(context)


# #############################################################################
#
# AJAX VIEWS
#
# #############################################################################

class IsSuperuser(BasePermission):
    """A permission to check if user is a superuser."""

    def has_permission(self, request, view):
        """
        Check whether user has superuser permission.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        view : rest_framework.views.APIView
            View that called the permission.

        Returns
        -------
        Boolean
            Indicating if user is a superuser.
        """
        return request.user and request.user.is_superuser


class SuperusersAjaxView(APIView):
    """Ajax API for all superusers."""

    permission_classes = (IsSuperuser,)

    def post(self, request):
        """
        Add a new superuser.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.response.Response
            Contains a list of superusers or an error message.
        """
        try:
            user = User.objects.get(pk=request.data.get('user_id'))
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
                'The user does not exist.',
                status=status.HTTP_400_BAD_REQUEST
            )


class SingleSuperuserAjaxView(APIView):
    """Ajax API for a single superuser."""

    permission_classes = (IsSuperuser,)

    def delete(self, request, user_id):
        """
        Delete a superuser.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        user_id : int
            Identifies the user in the database.

        Returns
        -------
        rest_framework.response.Response
            Empty response indicating success or an error message.
        """
        try:
            user = User.objects.get(pk=user_id, is_superuser=True)
            user.is_superuser = False
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                'The user does not exist.',
                status=status.HTTP_404_NOT_FOUND
            )
