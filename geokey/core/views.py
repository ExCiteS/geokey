"""Core views."""

from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin

from geokey.version import get_version
from geokey.extensions.base import extensions
from geokey.projects.views import ProjectContext
from geokey.core.models import LoggerHistory

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class LoggerList(LoginRequiredMixin, ProjectContext, TemplateView):
    """A list of all history logs."""

    template_name = 'logger/logger_list.html'

    def get_context_data(self, project_id, *args, **kwargs):
        """
        Return the context to render the view.
        Parameters
        ----------
        project_id : int
            Identifies the project in the database.
        Returns
        -------
        dict
            Context.
        """

        context = super(LoggerList, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        logs = LoggerHistory.objects.filter(
            project__contains={'id': str(project_id)})

        context['logs'] = self.paginate_logs(
            logs[::-1],
            self.request.GET.get('page'))

        return context

    def paginate_logs(self, logs, page):
            """Paginate all logs."""
            paginator = Paginator(logs, 20)

            try:
                logs = paginator.page(page)
            except PageNotAnInteger:
                logs = paginator.page(1)
            except EmptyPage:
                logs = paginator.page(paginator.num_pages)

            return logs


# ############################################################################
#
# PUBLIC API
#
# ############################################################################

class InfoAPIView(APIView):
    """Public API for GeoKey server information."""

    def get(self, request):
        """
        Handle GET request.

        Return GeoKey server information.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.response.Response
            Contains the GeoKey server information.
        """
        info = {'geokey': {}}
        info['geokey']['version'] = get_version()
        info['geokey']['installed_extensions'] = map(
            lambda (ext_id, ext): {
                'name': ext_id,
                'version': ext['version'] if 'version' in ext else None
            },
            extensions.iteritems()
        )

        return Response(info)
