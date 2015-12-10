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
        # GeoKey version:
        info['geokey_version'] = get_version()
        # Installed extensions (only the ids):
        info['installed_extensions'] = map(lambda ext: ext, extensions)
        # TODO Add extension versions?
        # TODO Add more info later?
        
        # Return info:
        return Response(info)
