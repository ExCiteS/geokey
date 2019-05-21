"""Models for applications."""

try:
    # Python 3
    from re import fullmatch
except ImportError:
    # Python 2
    def fullmatch(regex, string, flags=0):
        from re import match
        return match('(?:' + regex + r')\Z', string, flags=flags)

try:
    # Python 3
    from urllib.parse import urlparse, parse_qsl
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qsl

from django.db import models

from oauth2_provider.models import AbstractApplication

from .base import STATUS
from .managers import ApplicationManager


class Application(AbstractApplication):
    """
    Represents an application, that is registered in order to interact with
    GeoKey platform.
    """

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    download_url = models.URLField(blank=False)

    objects = ApplicationManager()

    def redirect_uri_allowed(self, uri):
        """
        Check if redirect URI is allowed, it can now be a regular expression,
        e.g: `https://(.*).example.com` will match all subdomains.
        """
        for allowed_uri in self.redirect_uris.split():
            parsed_allowed_uri = urlparse(allowed_uri)
            parsed_uri = urlparse(uri)

            if all([
                parsed_allowed_uri.scheme == parsed_uri.scheme,
                fullmatch(parsed_allowed_uri.netloc, parsed_uri.netloc),
                parsed_allowed_uri.path == parsed_uri.path,
            ]):
                aqs_set = set(parse_qsl(parsed_allowed_uri.query))
                uqs_set = set(parse_qsl(parsed_uri.query))

                if aqs_set.issubset(uqs_set):
                    return True

        return False
