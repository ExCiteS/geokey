"""Development settings."""

from .base import *

# Development environment should have debugging enabled
DEBUG = True
DEBUG_TOOLBAR = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
# (see http://docs.djangoproject.com/en/1.8/ref/settings/#template-debug)
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG

STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# Output email on the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching while in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INSTALLED_APPS += (
    'django_nose',
)

# Django Debug Toolbar (see http://django-debug-toolbar.readthedocs.org)
DEBUG_TOOLBAR_PATCH_SETTINGS = False
INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'geokey.core.middleware.show_debug_toolbar'
}

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# set up django-devserver if installed
try:
    import devserver
    INSTALLED_APPS = (
        'devserver',
    ) + INSTALLED_APPS
    # more details at https://github.com/dcramer/django-devserver#configuration
    DEVSERVER_DEFAULT_ADDR = '0.0.0.0'
    DEVSERVER_DEFAULT_ADDR
    DEVSERVER_DEFAULT_PORT = '8000'
    DEVSERVER_AUTO_PROFILE = False  # use decorated functions
    DEVSERVER_TRUNCATE_SQL = True  # squash verbose output, show from/where
    DEVSERVER_MODULES = (
        # uncomment if you want to show every SQL executed
        # 'devserver.modules.sql.SQLRealTimeModule',
        # show sql query summary
        'devserver.modules.sql.SQLSummaryModule',
        # Total time to render a request
        'devserver.modules.profile.ProfileSummaryModule',

        # Modules not enabled by default
        # 'devserver.modules.ajax.AjaxDumpModule',
        # 'devserver.modules.profile.MemoryUseModule',
        # 'devserver.modules.cache.CacheSummaryModule',
        # see documentation for line profile decorator examples
        # 'devserver.modules.profile.LineProfilerModule',
        # show django session information
        # 'devserver.modules.request.SessionInfoModule',
    )

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'testing@example.com'
except ImportError:
    pass
