from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

from braces.views import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework import status

from projects.models import Project
from users.models import User
from users.serializers import UserSerializer


# #############################################################################
#
# ADMIN VIEWS
#
# #############################################################################


class SuperuserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.render_to_response({
                'error_description': 'Superuser tools are for superusers only.'
                                     ' You are not a superuser.',
                'error': 'Permission denied.'
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)


class PlatformSettings(LoginRequiredMixin, SuperuserMixin, TemplateView):
    template_name = 'superusertools/platform_settings.html'

    def get_context_data(self):
        return {'site': get_current_site(self.request)}

    def post(self, request):
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
    template_name = 'superusertools/projects_list.html'

    def get_context_data(self):
        return {'projects': Project.objects.all()}


class ManageSuperUsers(LoginRequiredMixin, SuperuserMixin, TemplateView):
    template_name = 'superusertools/manage_users.html'

    def get_context_data(self):
        return {'superusers': User.objects.filter(is_superuser=True)}


# #############################################################################
#
# ADMIN AJAX VIEWS
#
# #############################################################################


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class AddSuperUsersAjaxView(APIView):
    permission_classes = (IsSuperUser,)

    def post(self, request, format=None):
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
    permission_classes = (IsSuperUser,)

    def delete(self, request, user_id, format=None):
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
