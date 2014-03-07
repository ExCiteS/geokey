from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project

from .base import STATUS
from .forms import ViewCreateForm, ViewGroupCreateForm
from .models import View, ViewGroup
from .serializers import ViewUpdateSerializer, ViewGroupUpdateSerializer


class ViewAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create view page
    """
    form_class = ViewCreateForm
    template_name = 'views/view_create.html'

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:view_settings',
            kwargs={'project_id': project_id, 'view_id': self.object.id}
        )

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            ViewAdminCreateView, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, pk=project_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, pk=project_id)

        form.instance.project = project
        form.instance.creator = self.request.user
        return super(ViewAdminCreateView, self).form_valid(form)


class ViewAdminSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'views/view_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        view = View.objects.as_admin(user, project_id, view_id)
        return {'view': view, 'status_types': STATUS}


class ViewAdminDataView(LoginRequiredMixin, TemplateView):
    template_name = 'views/view_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        view = View.objects.get_single(user, project_id, view_id)
        return {'view': view}


class ViewApiDetail(APIView):
    """
    API Endpoints for a view in the AJAX API.
    /ajax/projects/:project_id/views/:view_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, view_id, format=None):
        """
        Updates a view
        """
        view = View.objects.as_admin(request.user, project_id, view_id)
        serializer = ViewUpdateSerializer(view, data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, format=None):
        """
        Deletes a view
        """
        view = View.objects.as_admin(request.user, project_id, view_id)
        view.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ViewGroupAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create usergroup page
    """
    form_class = ViewGroupCreateForm
    template_name = 'views/view_group_create.html'

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']
        group_id = self.object.id
        return reverse(
            'admin:view_group_settings',
            kwargs={
                'project_id': project_id,
                'view_id': view_id,
                'group_id': group_id
            }
        )

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']

        context = super(
            ViewGroupAdminCreateView, self).get_context_data(**kwargs)

        context['view'] = View.objects.as_admin(
            self.request.user, project_id, view_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the view group.
        """
        project_id = self.kwargs['project_id']
        view_id = self.kwargs['view_id']
        view = View.objects.as_admin(self.request.user, project_id, view_id)

        form.instance.view = view
        return super(ViewGroupAdminCreateView, self).form_valid(form)


class ViewGroupAdminSettingsView(LoginRequiredMixin, TemplateView):
    """
    Displays the usergroup admin page
    """
    template_name = 'views/view_group_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, view_id, group_id, **kwargs):
        """
        Creates the request context for rendering the page
        """

        context = super(
            ViewGroupAdminSettingsView, self).get_context_data(**kwargs)

        context['group'] = ViewGroup.objects.as_admin(
            self.request.user, project_id, view_id, group_id
        )
        return context


class ViewUserGroupApiDetail(APIView):
    """
    API Endpoints for a view in the AJAX API.
    /ajax/projects/:project_id/views/:view_id/usergroups/:group_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, view_id, group_id, format=None):
        """
        Updates a view
        """
        group = ViewGroup.objects.as_admin(
            request.user, project_id, view_id, group_id)
        serializer = ViewGroupUpdateSerializer(group, data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, group_id, format=None):
        """
        Deletes a view
        """
        group = ViewGroup.objects.as_admin(
            request.user, project_id, view_id, group_id)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
