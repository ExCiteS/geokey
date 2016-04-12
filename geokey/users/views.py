"""Views for users."""

from json import loads as json_loads
from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

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
            return redirect('admin:dashboard')

        return super(Index, self).get(request, *args, **kwargs)


class Dashboard(LoginRequiredMixin, TemplateView):
    """Dashboard page."""

    template_name = 'dashboard.html'

    def get_context_data(self):
        """
        Return the context to render the view.

        Overwrite the method to add projects, project status types and
        extensions to the context.

        Returns
        -------
        dict
        """
        from geokey.extensions.base import extensions

        ext = []
        for ext_id in sorted(extensions):
            extension = extensions.get(ext_id)
            if extension.get('display_admin') and (
                    not extension.get('superuser') or
                    self.request.user.is_superuser):
                ext.append(extension)

        return {
            'projects': Project.objects.get_list(
                self.request.user).filter(admins=self.request.user),
            'status_types': STATUS,
            'extensions': ext
        }


class UserGroupList(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Displays the list of user groups in the project.
    """
    template_name = 'users/usergroup_list.html'


class UserGroupCreate(LoginRequiredMixin, ProjectContext, CreateView):

    """
    Provides the form to create a new user group.
    """
    template_name = 'users/usergroup_create.html'
    form_class = UsergroupCreateForm

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Overwrites the method to add project to the context.

        Returns
        -------
        dict
            Context
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
            kwargs={'project_id': project_id, 'usergroup_id': self.object.id}
        )

    def form_valid(self, form):
        """
        Creates the user group.

        Parameter
        ---------
        form : geokey.users.forms.UsergroupCreateForm
            Represents the user input
        """

        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project

        add_another_url = reverse(
            'admin:usergroup_create',
            kwargs={
                'project_id': project_id
            }
        )

        messages.success(
            self.request,
            mark_safe('The user group has been created. <a href="%s">Add '
                      'another user group.</a>' % add_another_url)
        )

        return super(UserGroupCreate, self).form_valid(form)

    def post(self, request, project_id, *args, **kwargs):
        """
        Creates the user group.

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
            cannot_create = 'New user groups cannot be created.'

            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. %s' % cannot_create
                )
            else:
                return super(UserGroupCreate, self).post(
                    request, project_id, *args, **kwargs
                )

        return self.render_to_response(context)


class AdministratorsOverview(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Displays the project admins overview page.
    """
    template_name = 'users/usergroup_admins.html'


class UserGroupContext(object):

    """
    Mixin that provides the context to render templates. The context contains
    a user group instance based on project_id and subset_id.
    """

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, usergroup_id, *args, **kwargs):
        """
        Returns the context containing the project and user group instances,
        also status types.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        dict
            Context
        """

        project = Project.objects.as_admin(self.request.user, project_id)
        usergroup = project.usergroups.get(pk=usergroup_id)

        return super(UserGroupContext, self).get_context_data(
            project=project,
            usergroup=usergroup,
            status_types=STATUS,
            *args,
            **kwargs
        )


class UserGroupOverview(LoginRequiredMixin, UserGroupContext, TemplateView):

    """
    Displays the user group overview (members) page.
    """
    template_name = 'users/usergroup_overview.html'


class UserGroupSettings(LoginRequiredMixin, UserGroupContext, TemplateView):

    """
    Provides the form to update the user group settings.
    """
    template_name = 'users/usergroup_settings.html'

    def post(self, request, project_id, usergroup_id):
        """
        Updates the user group based on the data entered by the user.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template when user group updated
        django.http.HttpResponse
            Rendered template, if project or user group does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id, usergroup_id)
        usergroup = context.get('usergroup')

        if usergroup:
            usergroup.name = strip_tags(data.get('name'))
            usergroup.description = strip_tags(data.get('description'))
            usergroup.save()

            messages.success(self.request, 'The user group has been updated.')

        return self.render_to_response(context)


class UserGroupData(LoginRequiredMixin, UserGroupContext, TemplateView):

    """
    Provides the form to change the filter settings for the user group.
    """
    template_name = 'users/usergroup_data.html'

    def post(self, request, project_id, usergroup_id):
        """
        Updates the user group filter based on the data entered by the user.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template when user group updated
        django.http.HttpResponse
            Rendered template, if project or user group does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id, usergroup_id)
        usergroup = context.get('usergroup')

        if usergroup:
            cannot_modify = 'User group data cannot be modified.'

            if usergroup.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. %s' % cannot_modify
                )
            elif usergroup.project.categories.count() == 0:
                messages.error(
                    self.request,
                    'The project has no categories. %s' % cannot_modify
                )
            else:
                if data['filters'] != '-1':
                    if data['permission'] == 'all':
                        usergroup.filters = None
                    else:
                        usergroup.filters = json_loads(data['filters'])

                    usergroup.save()

                    messages.success(
                        self.request,
                        'The user group has been updated.'
                    )

        return self.render_to_response(context)


class UserGroupPermissions(LoginRequiredMixin, UserGroupContext, TemplateView):

    """
    Provides the form to update the user group permissions.
    """
    template_name = 'users/usergroup_permissions.html'

    def post(self, request, project_id, usergroup_id):
        """
        Updates the user group permissions based on the data entered by the
        user.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template when user group updated
        django.http.HttpResponse
            Rendered template, if project or user group does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id, usergroup_id)
        usergroup = context.get('usergroup')

        if usergroup:
            cannot_modify = 'User group permissions cannot be modified.'

            if usergroup.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. %s' % cannot_modify
                )
            else:
                usergroup.can_moderate = False
                usergroup.can_contribute = False

                if data['permission'] == 'can_moderate':
                    usergroup.can_moderate = True
                elif data['permission'] == 'can_contribute':
                    usergroup.can_contribute = True

                usergroup.save()

                messages.success(
                    self.request,
                    'The user group has been updated.'
                )

        return self.render_to_response(context)


class UserGroupDelete(LoginRequiredMixin, UserGroupContext, TemplateView):

    """
    Deletes the user group.
    """
    template_name = 'base.html'

    def get(self, request, project_id, usergroup_id):
        """
        Deletes the user group.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to user group list if user group is deleted, user group
            settings if project is locked
        django.http.HttpResponse
            Rendered template, if project or user group does not exist
        """

        context = self.get_context_data(project_id, usergroup_id)
        usergroup = context.get('usergroup')

        if usergroup:
            if usergroup.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. User group cannot be deleted.'
                )
                return redirect(
                    'admin:usergroup_settings',
                    project_id=project_id,
                    usergroup_id=usergroup_id
                )
            else:
                usergroup.delete()

                messages.success(
                    self.request,
                    'The user group has been deleted.'
                )

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

        Parameters
        ----------
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
    AJAX endpoint for querying a list of users in the AJAX API.
    """

    def get(self, request):
        """
        Returns a list of users where the `display_name` matches the query.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the HTTP request

        Returns
        -------
        rest_framework.response.Response
            Contains the list of users
        """

        q = request.GET.get('query')

        if q is None:
            return Response([])
        else:
            users = User.objects.filter(
                display_name__icontains=q.lower()
            ).exclude(pk=1)[:10]

            serializer = UserSerializer(
                users, many=True, fields=('id', 'display_name')
            )
            return Response(serializer.data)


class UserGroup(APIView):

    """
    API endpoints for a user group of a project in the AJAX API.
    """

    @handle_exceptions_for_ajax
    def put(self, request, project_id, usergroup_id):
        """
        Updates user group information.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the HTTP request
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised user group or an error message
        """

        project = Project.objects.as_admin(request.user, project_id)

        if project.islocked:
            return Response(
                'The project is locked. User group info cannot be modified.',
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            group = project.usergroups.get(pk=usergroup_id)
            serializer = UserGroupSerializer(
                group, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupUsers(APIView):

    """
    API endpoints for users in a user group of a project in the AJAX API.
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, usergroup_id):
        """
        Adds a user to the user group.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the HTTP request
        project_id : int
            Identifies the project in the database
        usergroup_id : int
            Identifies the user group in the database

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised user group or an error message
        """

        project = Project.objects.as_admin(request.user, project_id)

        if project.islocked:
            return Response(
                'The project is locked. New users cannot be added',
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            user_id = request.data.get('user_id')

            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response(
                    'The user you are trying to add to the user group does ' +
                    'not exist',
                    status=status.HTTP_400_BAD_REQUEST
                )

            group = project.usergroups.get(pk=usergroup_id)
            group.users.add(user)

            serializer = UserGroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################


class CreateUserMixin(object):

    """
    Mixin to create a user.
    """

    def create_user(self, data):
        """
        Creates a user.

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
    API endpoint to get, update and create a user.
    """

    def get(self, request):
        """
        Returns the user information.

        Parameters
        ----------
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
        Updates the user information.

        Parameters
        ----------
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
        Creates a new user.

        Parameters
        ----------
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
    API endpoint to change the password via the client.
    """

    def post(self, request):
        """
        Updates the password.

        Parameters
        ----------
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
