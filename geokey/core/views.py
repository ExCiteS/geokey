from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.version import get_version

from geokey.extensions.base import extensions

# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################

class InfoAPIView(APIView):
    """
    API endpoint to get GeoKey server information
    """
    def get(self, request):
        """
        Returns GeoKey server information

        Parameter
        ---------
        request : rest_framework.request.Request
            Represents the HTTP request

        Response
        --------
        rest_framework.response.Response
            Containing the GeoKey server information
        """
        info = {}
        gk_info = info['geokey'] = {}
        # GeoKey version:
        gk_info['version'] = get_version()
        # Installed extensions (with their version):
        gk_info['installed_extensions'] = map(
            lambda (ext_id, ext): {
                'name': ext_id,
                'version': (ext['version'] if 'version' in ext else None)},
            filter(
                lambda (ext_id, ext):
                    request.user.is_superuser or not ext['superuser'],
                extensions.iteritems()))
        # TODO Add more info later?
        
        # Return info:
        return Response(info)
