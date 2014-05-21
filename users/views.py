from django.db.models import Q
from django.views.generic import TemplateView, CreateView
from django.contrib import auth
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from braces.views import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from projects.models import Project
from projects.base import STATUS
from applications.models import Application
from dataviews.models import View

from .serializers import (
    UserSerializer, UserGroupSerializer, ViewGroupSerializer
)
from .models import ViewUserGroup
from .forms import UserRegistrationForm, UsergroupCreateForm


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


class Login(TemplateView):
    """
    Displays the login page and handles login requests.
    """
    template_name = 'login.html'

    def get(self, request):
        """
        Displays the page and an optional message if the user has been
        redirected here from anonther page.
        """
        if request.GET and request.GET.get('next'):
            context = self.get_context_data(
                login_required=True,
                next=request.GET.get('next')
            )
        else:
            context = self.get_context_data
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Authenticates the user and redirects to next page if available.
        """
        user = auth.authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            auth.login(request, user)
            if request.GET and request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('admin:dashboard')
        else:
            context = self.get_context_data(login_failed=True)
            return self.render_to_response(context)


class Logout(TemplateView):
    """
    Displays the logout page
    """
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        """
        Logs the user out
        """
        auth.logout(request)
        return super(Logout, self).get(request, *args, **kwargs)

    def get_context_data(self):
        """
        Return the context data to display the 'Succesfully logged out message'
        """
        return {'logged_out': True}


class Signup(CreateView):
    """
    Displays the sign-up page
    """
    template_name = 'signup.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        """
        Registers the user if the form is valid and no other has been
        regstered woth the username.
        """
        data = form.cleaned_data
        User.objects.create_user(
            data.get('username'),
            data.get('email'),
            data.get('password'),
            last_name=data.get('last_name'),
            first_name=data.get('first_name'),
        ).save()

        user = auth.authenticate(
            username=data.get('username'),
            password=data.get('password')
        )

        auth.login(self.request, user)
        return redirect('admin:dashboard')

    def form_invalid(self, form):
        """
        The form is invalid or another user has already been registerd woth
        that username. Displays the error message.
        """
        context = self.get_context_data(form=form, user_exists=True)
        return self.render_to_response(context)


class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Displays the dashboard.
    """
    template_name = 'dashboard.html'

    def get_context_data(self):
        return {
            'projects': Project.objects.get_list(self.request.user),
            'apps': Application.objects.get_list(self.request.user),
            'status_types': STATUS
        }


class QueryUsers(APIView):
    def get(self, request, format=None):
        q = request.GET.get('query').lower()
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(last_name__icontains=q) |
            Q(first_name__icontains=q))[:10]

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserGroup(APIView):
    """
    API Endpoints for a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users
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


class UserGroupUser(APIView):
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
    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id, format=None):
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        try:
            view = project.views.get(pk=request.DATA.get('view'))
            ViewUserGroup.objects.create(view=view, usergroup=group)
            serializer = UserGroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except View.DoesNotExist:
            return Response(
                'The view you are trying to add to the user group is not'
                'assigned to this project.',
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupSingleView(APIView):
    def get_object(self, user, project_id, group_id, view_id):
        project = Project.objects.as_admin(user, project_id)
        group = project.usergroups.get(pk=group_id)
        return group.viewgroups.get(view_id=view_id)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, group_id, view_id, format=None):
        view_group = self.get_object(
            request.user, project_id, group_id, view_id)

        serializer = ViewGroupSerializer(
            view_group, data=request.DATA, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, view_id, format=None):
        view_group = self.get_object(
            request.user, project_id, group_id, view_id)
        view_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGroupCreate(LoginRequiredMixin, CreateView):
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
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:project_settings',
            kwargs={'project_id': project_id}
        )

    def form_valid(self, form):
        """
        Creates the project and redirects to the project overview page
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project
        return super(UserGroupCreate, self).form_valid(form)
