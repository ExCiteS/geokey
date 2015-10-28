from json import loads as json_loads
from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.html import strip_tags

from braces.views import LoginRequiredMixin

from allauth.account.models import EmailAddress

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from geokey.applications.models import Application

from geokey.projects.views import ProjectContext
from geokey.core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from geokey.projects.models import Project
from geokey.projects.base import STATUS

from .models import User
from .serializers import (UserSerializer, UserGroupSerializer)
from .forms import (
    UsergroupCreateForm,
    CustomPasswordChangeForm,
    UserRegistrationForm,
    UserForm
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
        """
        Renders the page or redirects to dashboard if user is authenticated.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.

        Returns
        -------
        django.http.HttpResponse
            Rendered template

        django.http.HttpResponseRedirect
            to dashboard, if the user is signed in
        """
        if not request.user.is_anonymous():
            #     return self.render_to_response(self.get_context_data)
            # else:
            return redirect('admin:dashboard')

        return super(Index, self).get(request, *args, **kwargs)


class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Displays the dashboard.
    """
    template_name = 'dashboard.html'

    def get_context_data(self):
        """
        Returns the context to render the view. Overwrites the method to add
        projects, projects status types and extensions to context

        Return
        dict
        """
        projects = Project.objects.get_list(self.request.user)

        from geokey.extensions.base import extensions
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


class UserGroupList(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Displays a list of all user groups for a project.
    """
    template_name = 'users/usergroup_list.html'


class UserGroupCreate(LoginRequiredMixin, ProjectContext, CreateView):
    """
    Displays the create user group page
    `/admin/projects/:project_id/usergroups/new/`
    """
    template_name = 'users/usergroup_create.html'
    form_class = UsergroupCreateForm

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Overwrites the method to add project to the context

        Returns
        -------
        dict
        """
        project_id = self.kwargs['project_id']

        return super(UserGroupCreate, self).get_context_data(project_id)

    def get_success_url(self):
        """
        Returns the redirect URL that is called after the user group has been
        created.

        Returns
        -------
        str
            URL that is called after the Group has been created
        """
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:usergroup_overview',
            kwargs={'project_id': project_id, 'group_id': self.object.id}
        )

    def form_valid(self, form):
        """
        Creates the user group

        Parameter
        ---------
        form : geokey.users.forms.UsergroupCreateForm
            Represents the user input
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project
        messages.success(self.request, "The user group has been created.")
        return super(UserGroupCreate, self).form_valid(form)

    def post(self, request, project_id, *args, **kwargs):
        """
        Creates the user group

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the data base

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        self.object = None
        context = self.get_context_data(*args, **kwargs)
        project = context.get('project')

        if project is not None:
            return super(UserGroupCreate, self).post(
                request, project_id, *args, **kwargs
            )

        return self.render_to_response(context)


class AdministratorsOverview(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Displays the list of administrators of the project
    `/admin/projects/:project_id/usergroups/:group_id/`
    """
    template_name = 'users/usergroup_admins.html'


class UserGroupMixin(object):
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page, adds the user group
        to the context

        Parameter
        ---------
        project_id : int
            identifies the project in the data base
        group_id : int
            identifies the group in the data base

        Returns
        -------
        dict
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        return super(UserGroupMixin, self).get_context_data(
            group=group,
            status_types=STATUS
        )


class UserGroupOverview(LoginRequiredMixin, UserGroupMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/`
    """
    template_name = 'users/usergroup_overview.html'


class UserGroupSettings(LoginRequiredMixin, UserGroupMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/settings/`
    """
    template_name = 'users/usergroup_settings.html'

    def post(self, request, project_id, group_id):
        """
        Updates the user group settings

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the data base
        group_id : int
            identifies the group in the data base

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        if group is not None:
            data = request.POST

            group.name = strip_tags(data.get('name'))
            group.description = strip_tags(data.get('description'))
            group.save()

            messages.success(self.request, "The user group has been updated.")
            context['group'] = group

        return self.render_to_response(context)


class UserGroupData(LoginRequiredMixin, UserGroupMixin, TemplateView):
    template_name = 'users/usergroup_data.html'

    def post(self, request, project_id, group_id):
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        if group is not None:
            data = request.POST

            if data['filters'] != '-1':
                if data['permission'] == 'all':
                    group.filters = None
                else:
                    group.filters = json_loads(data['filters'])
            group.save()
            context['group'] = group

        return self.render_to_response(context)


class UserGroupPermissions(LoginRequiredMixin, UserGroupMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/settings/`
    """
    template_name = 'users/usergroup_permissions.html'

    def post(self, request, project_id, group_id):
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        if group is not None:
            data = request.POST

            group.can_moderate = False
            group.can_contribute = False

            if data['permission'] == 'can_moderate':
                group.can_moderate = True
            elif data['permission'] == 'can_contribute':
                group.can_contribute = True

            group.save()

            messages.success(self.request, "The user group permissions have "
                                           "been updated.")
            context['group'] = group

        return self.render_to_response(context)


class UserGroupDelete(LoginRequiredMixin, UserGroupMixin, TemplateView):
    """
    Deletes the user group
    """
    template_name = 'base.html'

    def get(self, request, project_id, group_id):
        """
        Deletes the user group

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database
        group_id : int
            identifies the group in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            to the user group list

        django.http.HttpResponse
            If user is not administrator of the project, the error message is
            rendered.
        """

        context = self.get_context_data(project_id, group_id)
        group = context.get('group')

        if group is not None:
            group.delete()
            messages.success(self.request, 'The user group has been deleted.')
            return redirect('admin:usergroup_list', project_id=project_id)

        return self.render_to_response(context)


class UserProfile(LoginRequiredMixin, TemplateView):
    """
    Displays the user profile page.
    """
    template_name = 'users/profile.html'

    def post(self, request):
        """
        Updates user profile.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        user = User.objects.get(pk=request.user.pk)
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            if form.has_changed():
                user.display_name = form.cleaned_data['display_name']
                user.email = form.cleaned_data['email']
                user.save()

                if user.email != request.user.email:
                    try:
                        EmailAddress.objects.get(user=user).change(
                            request,
                            user.email,
                            confirm=True
                        )
                    except EmailAddress.DoesNotExist:
                        EmailAddress.objects.create(
                            user=user,
                            email=user.email
                        ).send_confirmation(request)

                messages.success(request, 'Your profile has been updated.')
                self.request.user = user
            else:
                messages.info(request, 'Your profile has not been edited.')

        return self.render_to_response(self.get_context_data(form=form))


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
    def get(self, request):
        """
        Returns a list of users where the display_name matches the query

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request

        Returns
        -------
        rest_framework.response.Response
            Contains the list of users
        """
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
    def put(self, request, project_id, group_id):
        """
        Updates user group information

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request
        project_id : int
            identifies the project in the database
        group_id : int
            identifies the group in the database

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised usergroup or an error message
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        serializer = UserGroupSerializer(
            group, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGroupUsers(APIView):
    """
    API Endpoints for users in a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users/
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id):
        """
        Adds a user to the usergroup

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request
        project_id : int
            identifies the project in the database
        group_id : int
            identifies the group in the database

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised usergroup or an error message
        """
        project = Project.objects.as_admin(request.user, project_id)
        user_id = request.data.get('userId')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                'The user you are trying to add to the user group does ' +
                'not exist',
                status=status.HTTP_400_BAD_REQUEST
            )

        group = project.usergroups.get(pk=group_id)
        group.users.add(user)

        serializer = UserGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserGroupSingleUser(APIView):
    """
    API Endpoints for a user in a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users/:user_id
    """

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, user_id):
        """
        Removes a user from the user group

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request
        project_id : int
            identifies the project in the database
        group_id : int
            identifies the group in the database
        user_id : int
            identifies the user in the database

        Returns
        -------
        rest_framework.response.Response
            Empty response if successful
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        user = group.users.get(pk=user_id)
        group.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################


class CreateUserMixin(object):
    """
    Mixin to create a user
    """
    def create_user(self, data):
        """
        Creates a user

        Parameters
        ----------
        data : dict
            User data

        Returns
        -------
        geokey.users.models.User
            The newly created user
        """
        user = User.objects.create_user(
            data.get('email'),
            data.get('display_name'),
            password=data.get('password1')
        )
        user.save()
        return user


class UserAPIView(CreateUserMixin, APIView):
    """
    API endpoint to get, update and create a user
    """
    def get(self, request):
        """
        Returns user information

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request

        Response
        --------
        rest_framework.response.Response
            Containing the user info or an error message if no user is signed
            in
        """
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
        """
        Updates user information

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request

        Response
        --------
        rest_framework.response.Response
            Containing the user info or an error message
        """
        user = request.user

        if user.is_anonymous():
            return Response(
                {'error': 'You have to be signed in to get user information'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        data = request.data

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            new_mail = data.get('email')

            if new_mail is not None and user.email != new_mail:
                try:
                    email = EmailAddress.objects.get(
                        user=user, email=user.email
                    )
                    email.change(request, new_mail, confirm=True)
                except EmailAddress.DoesNotExist:
                    EmailAddress.objects.create(user=user, email=new_mail)

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        """
        Creates a new user

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request

        Response
        --------
        rest_framework.response.Response
            Containing the user info or an error message
        """
        data = request.data
        form = UserRegistrationForm(data)
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


class ChangePasswordView(APIView):
    """
    API endpoint to change the password via the client
    """
    def post(self, request):
        """
        Updates the password

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request

        Response
        --------
        rest_framework.response.Response
            Empty response indicating success or error message
        """
        user = request.user
        data = request.data

        if not user.is_anonymous():
            form = CustomPasswordChangeForm(user, data)
            if form.is_valid():
                form.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': form.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'You have to be signed in to change the password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
