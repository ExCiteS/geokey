from json import loads as json_loads

from django.views.generic import TemplateView
from django.utils.html import strip_tags
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.views import ProjectContext
from geokey.projects.models import Project

from .models import Subset


class SubsetOverview(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Displays the list of subsets in a project.
    """
    template_name = 'subsets/subsets_overview.html'


class SubsetCreate(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Provides the form to create a new subset.
    """
    template_name = 'subsets/subsets_create.html'

    def post(self, request, project_id):
        """
        Creates the subset based on the data entered by the user

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the data base

        Returns
        -------
        django.http.HttpResponseRedirect
            to SubsetData
        django.http.HttpResponse
            Rendered template, if an error occured
        """
        data = request.POST
        context = self.get_context_data(project_id)

        project = context.get('project')

        if project:
            subset = Subset.objects.create(
                name=strip_tags(data.get('name')),
                description=strip_tags(data.get('description')),
                creator=request.user,
                project=project
            )
            messages.success(self.request, "The subset has been created.")
            return redirect(
                'admin:subset_data',
                project_id=project.id,
                subset_id=subset.id
            )
        else:
            return self.render_to_response(context)


class SubsetContext(object):
    """
    Mixin that provides the context to render templates. The context contains
    a Subset instance based on project_id and subset_id.
    """
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, subset_id, *args, **kwargs):
        """
        Returns the context containing the project instance.

        Parameters
        ----------
        project_id : int
            identifies the project in the data base
        subset_id : int
            identifies the subset in the data base

        Returns
        -------
        dict
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        subset = project.subsets.get(pk=subset_id)

        return super(SubsetContext, self).get_context_data(
            subset=subset,
            *args,
            **kwargs
        )


class SubsetSettings(LoginRequiredMixin, SubsetContext, TemplateView):
    """
    Provides the form to update the subset settings.
    """
    template_name = 'subsets/subsets_settings.html'

    def post(self, request, project_id, subset_id):
        """
        Updates the subset based on the data entered by the user

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the data base
        subset_id : int
            identifies the subset in the data base

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            data = request.POST
            subset.name = strip_tags(data.get('name'))
            subset.description = strip_tags(data.get('description'))
            subset.save()

            messages.success(self.request, "The subset has been updated.")

        return self.render_to_response(context)


class SubsetData(LoginRequiredMixin, SubsetContext, TemplateView):
    """
    Provides the form to change the filter settings for the subset
    """
    template_name = 'subsets/subsets_data.html'

    def post(self, request, project_id, subset_id):
        """
        Updates the subset filter based on the data entered by the user

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the data base
        subset_id : int
            identifies the subset in the data base

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            data = request.POST
            if data['filters'] != '-1':
                subset.filters = json_loads(data['filters'])
                subset.save()

            messages.success(self.request, "The subset has been updated.")

        return self.render_to_response(context)


class SubsetDelete(LoginRequiredMixin, SubsetContext, TemplateView):
    """
    Deletes a subset
    """
    template_name = 'base.html'

    def get(self, request, project_id, subset_id):
        """
        Deletes the subset

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the data base
        subset_id : int
            identifies the subset in the data base

        Returns
        -------
        django.http.HttpResponseRedirect
            to SubsetOverview
        django.http.HttpResponse
            Rendered template, if an error has occured
        """
        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            subset.delete()
            messages.success(self.request, "The subset has been deleted.")
            return redirect('admin:subset_list', project_id=project_id)

        return self.render_to_response(context)
