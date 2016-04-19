"""WSGI configuration."""

import os

from django.core.wsgi import get_wsgi_application


try:
    import local_settings
    settings_module = 'settings'
except ImportError:
    settings_module = 'geokey.core.settings.project'


os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
application = get_wsgi_application()
