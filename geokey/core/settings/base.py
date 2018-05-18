"""Base settings."""

from os.path import abspath, dirname, join, normpath
from django.contrib import messages

# The ID of the current site in the django_site database table
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#site-id
SITE_ID = 1

# Ensures that a trailing slash is always present in URLs
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-APPEND_SLASH
APPEND_SLASH = True

# Sets the default time zone
TIME_ZONE = 'UTC'

# Disbles Django's translation engine
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#use-i18n
USE_I18N = False

# Enables localised date formatting
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#use-l10n
USE_L10N = True

# A boolean that specifies if datetimes will be timezone-aware by default or not.
# see: A boolean that specifies if datetimes will be timezone-aware by default or not.
USE_TZ = True

# All Django applications installed. Includes Django modules, third-party
# packages and GeoKey modules. New third-party packages and GeoKey modules
# should be added here.
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#installed-apps
INSTALLED_APPS = (
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',

    # Third-party apps
    'django_hstore',
    'oauth2_provider',
    'easy_thumbnails',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework_gis',
    'django_crontab',

    # GeoKey apps
    'geokey.core',
    'geokey.projects',
    'geokey.categories',
    'geokey.contributions',
    'geokey.users',
    'geokey.applications',
    'geokey.superusertools',
    'geokey.extensions',
    'geokey.subsets',
    'geokey.socialinteractions',
)

# Middleware that is used with GeoKey to process HTTP requests and responses.
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-MIDDLEWARE_CLASSES
# Learn about Middleware: https://docs.djangoproject.com/en/1.8/topics/http/middleware/
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'geokey.core.middleware.XsSharing',
    'geokey.core.middleware.RequestProvider',
)

# Settings for django-oauth-toolkit
# see: https://django-oauth-toolkit.readthedocs.org/en/latest/settings.html
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Access private projects, contributions and other information',
        'write': 'Manage contributions, comments and media files'
    },
    'CLIENT_SECRET_GENERATOR_LENGTH': 40
}
OAUTH2_PROVIDER_APPLICATION_MODEL = 'applications.Application'

# Settings for Django REST Framework
# see: http://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
}

# Avaiable message tags; for use with Django's messages Framework
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#message-tags
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger'
}

# Settings for django.contrib.auth, used for user authentication
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#auth
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend'
)
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/admin/dashboard/'
LOGIN_URL = '/admin/account/login/'

# django-allauth settings
# see: http://django-allauth.readthedocs.org/en/latest/configuration.html
ACCOUNT_ADAPTER = 'geokey.core.adapters.AccountAdapter'
ACCOUNT_LOGOUT_REDIRECT_URL = '/admin/account/login/'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'display_name'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/admin/account/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/admin/dashboard/'
ACCOUNT_FORMS = {
    'signup': 'geokey.users.forms.UserRegistrationForm',
    'change_password': 'geokey.users.forms.CustomPasswordChangeForm',
    'reset_password_from_key': 'geokey.users.forms.CustomResetPasswordKeyForm'
}
SOCIALACCOUNT_ADAPTER = 'geokey.core.adapters.SocialAccountAdapter'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {}

SITE_ROOT = dirname(dirname(dirname(abspath(__file__))))
STATICFILES_DIRS = [normpath(join(SITE_ROOT, 'static'))]

ROOT_URLCONF = 'geokey.core.urls'

# Settings for Django's template engine
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [normpath(join(SITE_ROOT, 'templates'))],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'geokey.core.context_processors.project_settings',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

# Custom GeoKey settings, enables video upload. Disabled by default, can be
# endabled by overwriting in local settings
ENABLE_VIDEO = False

CRONJOBS = [
    ('*/5 * * * *', 'geokey.socialinteractions.utils.start2pull'),
]
