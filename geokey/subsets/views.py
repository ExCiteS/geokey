from json import loads as json_loads

from django.views.generic import TemplateView
from django.utils.html import strip_tags
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.models import Project

from .models import Subset


class ProjectContext(object):
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, *args, **kwargs):
        project = Project.objects.as_admin(self.request.user, project_id)

        return super(ProjectContext, self).get_context_data(
            project=project,
            *args,
            **kwargs
        )


class SubsetOverview(LoginRequiredMixin, ProjectContext, TemplateView):
    template_name = 'subsets/subsets_overview.html'


class SubsetCreate(LoginRequiredMixin, ProjectContext, TemplateView):
    template_name = 'subsets/subsets_create.html'

    def post(self, request, project_id):
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
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, subset_id, *args, **kwargs):
        project = Project.objects.as_admin(self.request.user, project_id)
        subset = project.subsets.get(pk=subset_id)

        return super(SubsetContext, self).get_context_data(
            subset=subset,
            *args,
            **kwargs
        )


class SubsetSettings(LoginRequiredMixin, SubsetContext, TemplateView):
    template_name = 'subsets/subsets_settings.html'

    def post(self, request, project_id, subset_id):
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
    template_name = 'subsets/subsets_data.html'

    def post(self, request, project_id, subset_id):
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
    template_name = 'base.html'

    def get(self, request, project_id, subset_id):
        context = self.get_context_data(project_id, subset_id)
        subset = context.get('subset')

        if subset:
            subset.delete()
            messages.success(self.request, "The subset has been deleted.")
            return redirect('admin:subset_list', project_id=project_id)

        return self.render_to_response(context)
