"""Core middleware."""
# https://gist.github.com/barrabinfc/426829

from django import http
from django.db import connection

try:
    import settings
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
    XS_SHARING_ALLOWED_HEADERS = settings.XS_SHARING_ALLOWED_HEADERS
except:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'PATCH', 'DELETE']
    XS_SHARING_ALLOWED_HEADERS = ['Authorization', 'Content-Type']


class XsSharing(object):
    """
    This middleware allows cross-domain XHR using the HTML5 postMessage API.

    Access-Control-Allow-Origin: http://foo.example
    Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
    """
    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
            response['Access-Control-Allow-Headers'] = ",".join(XS_SHARING_ALLOWED_HEADERS)
            return response

        return None

    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
        response['Access-Control-Allow-Headers'] = ",".join(XS_SHARING_ALLOWED_HEADERS)

        return response


class TerminalLogging(object):
    def process_response(self, request, response):
        from sys import stdout
        if stdout.isatty():
            for query in connection.queries :
                print "\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (query['time'],
                    " ".join(query['sql'].split()))
        return response


def show_debug_toolbar(request):
    """Custom function to determine whether to show the debug toolbar."""
    from django.conf import settings

    # Do not include the debug toolbar on Ajax requests
    if request.is_ajax():
        return False

    return bool(settings.DEBUG and settings.DEBUG_TOOLBAR)
