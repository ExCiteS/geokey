from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

from projects.models import Project
from core.decorators import handle_exceptions_for_admin


class SuperuserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.render_to_response({
                'error_description': 'Superuser tools are for superusers only.'
                                     ' You are not a superuser.',
                'error': 'Permission denied.'
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)


class ProjectsList(LoginRequiredMixin, SuperuserMixin, TemplateView):
    template_name = 'superusertools/projects_list.html'

    def get_context_data(self):
        return {'projects': Project.objects.all()}
