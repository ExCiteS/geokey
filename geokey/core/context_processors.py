"""Core context processors."""

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from geokey import version


def project_settings(request):
    GOOGLE_ANALYTICS = None

    if hasattr(settings, 'GOOGLE_ANALYTICS'):
        GOOGLE_ANALYTICS = settings.GOOGLE_ANALYTICS

    return {
        'DEBUG': settings.DEBUG,
        'PLATFORM_NAME': get_current_site(request).name,
        'GEOKEY_VERSION': version.get_version(),
        'GOOGLE_ANALYTICS': GOOGLE_ANALYTICS
    }
