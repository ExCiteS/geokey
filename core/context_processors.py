from django.conf import settings


def project_settings(request):
    return {
        'PLATFORM_NAME': settings.PLATFORM_NAME
    }
