"""
Django settings for opencomap project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import abspath, dirname, join, normpath
from django.contrib import messages

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
TEMPLATE_DIRS = (
    normpath(join(SITE_ROOT, 'templates')),
)
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Application definition

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

    # third-party apps
    'django_hstore',
    'oauth2_provider',
    'easy_thumbnails',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # geokey apps
    'geokey.projects',
    'geokey.categories',
    'geokey.contributions',
    'geokey.datagroupings',
    'geokey.users',
    'geokey.applications',
    'geokey.superusertools',
    'geokey.extensions',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'geokey.core.middleware.XsSharing',
    # 'core.middleware.TerminalLogging',
)

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'},
    'CLIENT_SECRET_GENERATOR_LENGTH': 40
}
OAUTH2_PROVIDER_APPLICATION_MODEL = 'applications.Application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
}

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger'
}

AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend"
)

SITE_ID = 1
LOGIN_REDIRECT_URL = '/admin/dashboard/'
LOGIN_URL = '/admin/account/login/'
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
    'signup': 'users.forms.UserRegistrationForm',
    'change_password': 'users.forms.CustomPasswordChangeForm',
    'reset_password_from_key': 'users.forms.CustomResetPasswordKeyForm'
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "geokey.core.context_processors.project_settings",
    "django.contrib.messages.context_processors.messages",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

APPEND_SLASH = True

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
