"""Views for superuser tools."""

from django.db.models import Q, Case, When, Sum, IntegerField
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from braces.views import LoginRequiredMixin
from allauth.account.models import EmailAddress
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.users.models import User
from geokey.users.serializers import UserSerializer
from geokey.projects.models import Project
from geokey.contributions.base import OBSERVATION_STATUS
from geokey.superusertools.base import IsSuperuser
from geokey.superusertools.mixins import SuperuserMixin


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
            in_total = len(active_users)

            for email in EmailAddress.objects.filter(user__in=active_users):
                email.verified = True
                email.set_as_primary(conditional=True)
                email.save()

            active_users.update(is_active=True)
            messages.success(
                self.request,
                '%s user(s) has been activated.' % in_total)
            context['inactive_users'] = User.objects.filter(is_active=False)

        return self.render_to_response(context)


class ManageProjects(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Manage projects page."""

    template_name = 'superusertools/manage_projects.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Add a list of projects to the context (with numbers in total of
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
        ).defer(
            'description',
            'everyone_contributes',
            'admins',
            'geographic_extent'
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
        Handle POST request.

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


class ProviderList(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """A list of all providers page."""

    template_name = 'superusertools/provider_list.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Add all providers to the context.

        Returns
        -------
        dict
        """
        return {'providers': providers.registry.get_list()}


class ProviderContext(LoginRequiredMixin, SuperuserMixin):
    """Context mixin that adds a provider to render the template."""

    def get_context_data(self, provider_id, *args, **kwargs):
        """
        Return the context to render the view.

        Add a provider and optional social app to the context.

        Parameters
        ----------
        provider_id : str
            Identifies the provider in the list of available providers.

        Returns
        -------
        dict
        """
        try:
            provider = providers.registry.by_id(provider_id)

            try:
                social_app = SocialApp.objects.get_current(
                    provider.id,
                    self.request
                )
            except SocialApp.DoesNotExist:
                social_app = None

            return super(ProviderContext, self).get_context_data(
                provider=provider,
                social_app=social_app,
                *args,
                **kwargs
            )
        except:
            return {
                'error': 'Not found.',
                'error_description': 'Provider not found.'
            }


class ProviderOverview(ProviderContext, TemplateView):
    """Overview of a provider page."""

    template_name = 'superusertools/provider_overview.html'

    def post(self, request, provider_id):
        """
        Handle POST request.

        Update or enable the social app.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        provider_id : str
            Identifies the provider in the list of available providers.

        Returns
        -------
        django.http.HttpResponse
        """
        data = request.POST
        context = self.get_context_data(provider_id)
        provider = context.get('provider')
        social_app = context.get('social_app')

        if social_app:
            social_app.client_id = data.get('client_id')
            social_app.secret = data.get('secret')
            social_app.key = data.get('key')
            social_app.save()
            messages.success(
                self.request,
                'Provider has been updated.'
            )
        else:
            social_app = SocialApp.objects.create(
                provider=provider.id,
                name=provider.name,
                client_id=data.get('client_id'),
                secret=data.get('secret'),
                key=data.get('key')
            )
            social_app.sites.add(get_current_site(request))
            messages.success(
                self.request,
                'Provider has been activated.'
            )

        context['social_app'] = social_app

        return self.render_to_response(context)


# #############################################################################
#
# AJAX API
#
# #############################################################################

class SuperusersAjaxView(APIView):
    """Ajax API for all superusers."""

    permission_classes = (IsSuperuser,)

    @handle_exceptions_for_ajax
    def post(self, request):
        """
        Handle POST request.

        Add a user to superusers.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.response.Response
            Response to the request.
        """
        user = User.objects.get(pk=request.data.get('user_id'))
        user.is_superuser = True
        user.save()

        serializer = UserSerializer(
            User.objects.filter(is_superuser=True),
            many=True
        )
        return Response(
            {'users': serializer.data},
            status=status.HTTP_201_CREATED
        )


class SingleSuperuserAjaxView(APIView):
    """Ajax API for a single superuser."""

    permission_classes = (IsSuperuser,)

    @handle_exceptions_for_ajax
    def delete(self, request, user_id):
        """
        Handle DELETE request.

        Remove a user from superusers.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        user_id : int
            Identifies the user in the database.

        Returns
        -------
        rest_framework.response.Response
            Response to the request.
        """
        user = User.objects.get(pk=user_id, is_superuser=True)
        user.is_superuser = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
