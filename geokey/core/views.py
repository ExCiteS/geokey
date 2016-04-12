"""Core views."""

from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.version import get_version
from geokey.extensions.base import extensions


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
            filter(
                lambda (ext_id, ext):
                    request.user.is_superuser or not ext['superuser'],
                extensions.iteritems()
            )
        )

        return Response(info)
