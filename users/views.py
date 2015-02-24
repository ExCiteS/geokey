from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.html import strip_tags
from django.contrib.auth.views import password_reset_confirm as reset_view

from braces.views import LoginRequiredMixin

from allauth.account.models import EmailAddress
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from applications.models import Application

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from projects.models import Project, Admins
from projects.base import STATUS
from datagroupings.models import Grouping

from .serializers import (
    UserSerializer, UserGroupSerializer, GroupingUserGroupSerializer
)
from .models import User, GroupingUserGroup
from .forms import (
    UsergroupCreateForm,
    CustomPasswordChangeForm
)


# ############################################################################
#
# ADMIN VIEWS
#
# ############################################################################


class Index(TemplateView):
    """
    Displays the splash page. Redirects to dashboard if a user is looged in.
    """
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return self.render_to_response(self.get_context_data)
        else:
            return redirect('admin:dashboard')


class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Displays the dashboard.
    """
    template_name = 'dashboard.html'

    def get_context_data(self):
        projects = Project.objects.get_list(self.request.user)

        from extensions.base import extensions
        ext = []
        for ext_id in extensions.keys():
            extension = extensions.get(ext_id)

            if extension.get('display_admin') and (
                    not extension.get('superuser') or
                    self.request.user.is_superuser):
                ext.append(extension)

        return {
            'admin_projects': projects.filter(admins=self.request.user),
            'involved_projects': projects.exclude(
                admins=self.request.user).exists(),
            'status_types': STATUS,
            'extensions': ext
        }


class CreateUserMixin(object):
    def create_user(self, data):
        user = User.objects.create_user(
            data.get('email'),
            data.get('username'),
            password=data.get('password1')
        )
        user.save()
        return user


class UserAPIView(CreateUserMixin, APIView):
    def get(self, request):
        user = request.user
        if not user.is_anonymous():
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'You have to be signed in to get user information'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def patch(self, request):
        user = request.user

        if not user.is_anonymous():
            data = request.DATA
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()

                if data.get('password') is not None:
                    user.reset_password(data.get('password'))

                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'You have to be signed in to get user information'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def post(self, request):
        data = request.DATA
        form = SignupForm(data)
        client_id = data.pop('client_id', None)

        try:
            Application.objects.get(client_id=client_id)
            if form.is_valid():
                user = self.create_user(data)

                EmailAddress.objects.add_email(
                    request._request,
                    user,
                    user.email,
                    signup=True,
                    confirm=True
                )

                serializer = UserSerializer(user)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'errors': form.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Application.DoesNotExist:
            return Response(
                {'errors': {'client': 'Client ID not provided or incorrect.'}},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupList(LoginRequiredMixin, TemplateView):
    template_name = 'users/usergroup_list.html'

    def get_context_data(self, project_id):
        project = Project.objects.as_admin(self.request.user, project_id)
        return super(UserGroupList, self).get_context_data(project=project)


class UserGroupCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create user group page
    `/admin/projects/:project_id/usergroups/new/`
    """
    template_name = 'users/usergroup_create.html'
    form_class = UsergroupCreateForm

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            UserGroupCreate, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, project_id
        )
        return context

    def get_success_url(self):
        """
        Returns the redirect URL that is called after the user group has been
        created.
        """
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:usergroup_overview',
            kwargs={'project_id': project_id, 'group_id': self.object.id}
        )

    def form_valid(self, form):
        """
        Creates the project and redirects to the project overview page
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project
        messages.success(self.request, "The user group has been created.")
        return super(UserGroupCreate, self).form_valid(form)


class UserGroupOverview(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/`
    """
    template_name = 'users/usergroup_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        return {'group': group, 'status_types': STATUS}


class AdministratorsOverview(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/`
    """
    template_name = 'users/usergroup_admins.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return {'project': project}


class UserGroupSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/settings/`
    """
    template_name = 'users/usergroup_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        return {'group': group, 'status_types': STATUS}

    def post(self, request, project_id, group_id):
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        data = request.POST

        group.name = strip_tags(data.get('name'))
        group.description = strip_tags(data.get('description'))
        group.save()

        messages.success(self.request, "The user group has been updated.")
        context['group'] = group
        return self.render_to_response(context)


class UserGroupPermissions(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/settings/`
    """
    template_name = 'users/usergroup_permissions.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        return super(UserGroupPermissions, self).get_context_data(group=group)


class UserGroupDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        return super(UserGroupDelete, self).get_context_data(group=group)

    def get(self, request, project_id, group_id):
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        if group is not None:
            group.delete()

        messages.success(self.request, 'The user group has been deleted.')
        return redirect('admin:usergroup_list', project_id=project_id)


class UserProfile(LoginRequiredMixin, TemplateView):
    """
    Displays the user profile page
    `/admin/profile`
    """
    template_name = 'users/profile.html'

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Creates the request context for rendering the page
        """
        context = super(UserProfile, self).get_context_data(**kwargs)

        referer = self.request.META.get('HTTP_REFERER')
        if referer is not None and 'profile/password/change' in referer:
            context['password_reset'] = True

        return context

    def post(self, request):
        """
        Updates the user information
        """
        user = request.user

        user.email = request.POST.get('email')
        user.display_name = request.POST.get('display_name')

        user.save()

        context = self.get_context_data()
        messages.success(request, 'The user information has been updated.')
        return self.render_to_response(context)


class UserNotifications(LoginRequiredMixin, TemplateView):
    """
    Displays the notifications settings page
    `/admin/profile/notifications/`
    """
    template_name = 'users/notifications.html'

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        user = self.request.user

        context = super(UserNotifications, self).get_context_data(**kwargs)
        context['admins'] = Admins.objects.filter(user=user)

        return context

    @handle_exceptions_for_admin
    def post(self, request):
        context = self.get_context_data()
        data = self.request.POST

        for project in context.get('admins'):
            new_val = data.get(str(project.project.id)) is not None

            if project.contact != new_val:
                project.contact = new_val
                project.save()

        messages.success(request, 'Notifications have been updated.')
        return self.render_to_response(context)


def password_reset_confirm(request, *args, **kwargs):
    return reset_view(
        request,
        set_password_form=CustomPasswordChangeForm,
        *args,
        **kwargs
    )


# ############################################################################
#
# AJAX VIEWS
#
# ############################################################################

class QueryUsers(APIView):
    """
    AJAX endpoint for querying a list of users
    `/ajax/users/?query={username}
    """
    def get(self, request, format=None):
        q = request.GET.get('query').lower()
        users = User.objects.filter(
            display_name__icontains=q).exclude(pk=1)[:10]

        serializer = UserSerializer(
            users, many=True, fields=('id', 'display_name')
        )
        return Response(serializer.data)


class UserGroup(APIView):
    """
    API Endpoints for a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, group_id, format=None):
        """
        Updates user group information
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        serializer = UserGroupSerializer(
            group, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, format=None):
        """
        Deletes a user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGroupUsers(APIView):
    """
    API Endpoints for users in a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users/
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id, format=None):
        """
        Adds a user to the usergroup
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

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


class UserGroupSingleUser(APIView):
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
        group = project.usergroups.get(pk=group_id)

        user = group.users.get(pk=user_id)
        group.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGroupViews(APIView):
    """
    AJAX API endpoint for views assigned to the user group
    `/ajax/project/:project_id/usergroups/:group_id/views/`
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id, format=None):
        """
        Assigns a new view to the user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        try:
            grouping = project.groupings.get(pk=request.DATA.get('grouping'))
            view_group = GroupingUserGroup.objects.create(
                grouping=grouping,
                usergroup=group
            )
            serializer = GroupingUserGroupSerializer(
                view_group, data=request.DATA, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Grouping.DoesNotExist:
            return Response(
                'The data grouping you are trying to add to the user group is'
                'not assigned to this project.',
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupSingleView(APIView):
    """
    AJAX API endpoint for views assigned to the user group
    `/ajax/project/:project_id/usergroups/:group_id/views/:grouping_id/`
    """
    def get_object(self, user, project_id, group_id, grouping_id):
        project = Project.objects.as_admin(user, project_id)
        group = project.usergroups.get(pk=group_id)
        return group.viewgroups.get(grouping_id=grouping_id)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, group_id, grouping_id, format=None):
        """
        Updates the relation between user group and view, e.g. granting
        permissions on the view to the user group members.
        """
        view_group = self.get_object(
            request.user, project_id, group_id, grouping_id)

        serializer = GroupingUserGroupSerializer(
            view_group, data=request.DATA, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, grouping_id, format=None):
        """
        Removes the relation between usergroup and view.
        """
        view_group = self.get_object(
            request.user, project_id, group_id, grouping_id)
        view_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################

# N/A
