from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


def project_settings(request):
    return {
        'PLATFORM_NAME': get_current_site(request).name,
        'DEBUG': settings.DEBUG
    }
