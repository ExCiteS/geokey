"""Core views."""

from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.generic import TemplateView

from geokey.version import get_version
from geokey.extensions.base import extensions
from geokey.projects.views import ProjectContext
from geokey.core.models import LoggerHistory


class LoggerList(ProjectContext, TemplateView):
    """A list of all history logs."""

    template_name = 'logger/logger_list.html'

    def get_context_data(self, *args, **kwargs):
        """Return the context to render the view.
        Overwrite the method to add the logs for the to the context.
        Returns
        -------
        dict
            Context.
        """

        context = super(LoggerList, self).get_context_data(
            *args,
            **kwargs
        )

        logs = LoggerHistory.objects.filter(
            project__contains={'id': str(context['project'].id)})

        context['logs'] = logs[::-1]

        return context


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
