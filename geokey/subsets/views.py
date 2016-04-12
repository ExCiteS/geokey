"""Views for subsets."""

from json import loads as json_loads

from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.models import Project
from geokey.projects.views import ProjectContext

from .models import Subset


class SubsetList(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Displays the list of subsets in the project.
    """
    template_name = 'subsets/subset_list.html'


class SubsetCreate(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Provides the form to create a new subset.
    """
    template_name = 'subsets/subset_create.html'

    def post(self, request, project_id):
        """
        Creates the subset based on the data entered by the user.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to subset create if subset is created, subset list if
            project is locked or it does not have any categories
        django.http.HttpResponse
            Rendered template, if project does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id)
        project = context.get('project')

        if project:
            cannot_create = 'New subsets cannot be created.'

            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. %s' % cannot_create
                )
                return redirect(
                    'admin:subset_create',
                    project_id=project_id
                )
            elif project.categories.count() == 0:
                messages.error(
                    self.request,
                    'The project has no categories. %s' % cannot_create
                )
                return redirect(
                    'admin:subset_create',
                    project_id=project_id
                )
            else:
                subset = Subset.objects.create(
                    name=strip_tags(data.get('name')),
                    description=strip_tags(data.get('description')),
                    creator=request.user,
                    project=project
                )

                add_another_url = reverse(
                    'admin:subset_create',
                    kwargs={
                        'project_id': project_id
                    }
                )

                messages.success(
                    self.request,
                    mark_safe('The subset has been created. <a href="%s">Add '
                              'another subset.</a>' % add_another_url)
                )

                return redirect(
                    'admin:subset_data',
                    project_id=project_id,
                    subset_id=subset.id
                )
        else:
            return self.render_to_response(context)


class SubsetContext(object):

    """
    Mixin that provides the context to render templates. The context contains
    a subset instance based on project_id and subset_id.
    """

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, subset_id, *args, **kwargs):
        """
        Returns the context containing the project and subset instances.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database
        subset_id : int
            Identifies the subset in the database

        Returns
        -------
        dict
            Context
        """

        project = Project.objects.as_admin(self.request.user, project_id)
        subset = project.subsets.get(pk=subset_id)

        return super(SubsetContext, self).get_context_data(
            project=project,
            subset=subset,
            *args,
            **kwargs
        )


class SubsetSettings(LoginRequiredMixin, SubsetContext, TemplateView):

    """
    Provides the form to update the subset settings.
    """
    template_name = 'subsets/subset_settings.html'

    def post(self, request, project_id, subset_id):
        """
        Updates the subset based on the data entered by the user.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        subset_id : int
            Identifies the subset in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template when subset updated
        django.http.HttpResponse
            Rendered template, if project or subset does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            subset.name = strip_tags(data.get('name'))
            subset.description = strip_tags(data.get('description'))
            subset.save()

            messages.success(self.request, 'The subset has been updated.')

        return self.render_to_response(context)


class SubsetData(LoginRequiredMixin, SubsetContext, TemplateView):

    """
    Provides the form to change the filter settings for the subset.
    """
    template_name = 'subsets/subset_data.html'

    def post(self, request, project_id, subset_id):
        """
        Updates the subset filter based on the data entered by the user.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        subset_id : int
            Identifies the subset in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template when subset updated
        django.http.HttpResponse
            Rendered template, if project or subset does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            cannot_modify = 'Subset data cannot be modified.'

            if subset.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. %s' % cannot_modify
                )
            elif subset.project.categories.count() == 0:
                messages.error(
                    self.request,
                    'The project has no categories. %s' % cannot_modify
                )
            else:
                if data['filters'] != '-1':
                    subset.filters = json_loads(data['filters'])
                    subset.save()

                    messages.success(
                        self.request,
                        'The subset has been updated.'
                    )

        return self.render_to_response(context)


class SubsetDelete(LoginRequiredMixin, SubsetContext, TemplateView):

    """
    Deletes the subset.
    """
    template_name = 'base.html'

    def get(self, request, project_id, subset_id):
        """
        Deletes the subset.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        subset_id : int
            Identifies the subset in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to subset list if subset is deleted, subset settings if
            project is locked
        django.http.HttpResponse
            Rendered template, if project or subset does not exist
        """

        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            if subset.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Subset cannot be deleted.'
                )
                return redirect(
                    'admin:subset_settings',
                    project_id=project_id,
                    subset_id=subset_id
                )
            else:
                subset.delete()

                messages.success(self.request, 'The subset has been deleted.')
                return redirect('admin:subset_list', project_id=project_id)

        return self.render_to_response(context)
