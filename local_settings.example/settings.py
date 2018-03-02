"""GeoKey settings."""

import os
from geokey.core.settings.dev import *

# Default email, used for automated correspondence
DEFAULT_FROM_EMAIL = 'sender@example.com'
# django-allauth setting - determines the email verification method
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geokey',
        'USER': 'django',
        'PASSWORD': 'django123',
        'HOST': os.environ.get('DJANGO_DATABASE_HOST', 'localhost'),
        'PORT': '',
    }
}

# Your server's secret key
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Google Analytics tracking code (optional)
GOOGLE_ANALYTICS = ''

# Set this to `True`, if you want to enable video upload to YouTube
ENABLE_VIDEO = False

# YouTube account settings (must be set if you enable video uploads)
# https://developers.google.com/youtube/registering_an_application
YOUTUBE_AUTH_EMAIL = 'your-email@example.com'
YOUTUBE_AUTH_PASSWORD = 'password'
YOUTUBE_DEVELOPER_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
YOUTUBE_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'

# Additional Django packages and GeoKey extensions
INSTALLED_APPS += (
    # ...
)

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = '/geokey/static/'
STATIC_URL = '/static/'

# Media files (usually uploaded by the user)
MEDIA_ROOT = normpath(join(dirname(dirname(abspath(__file__))), 'assets'))
MEDIA_URL = '/assets/'

# Python path to WSGI application
WSGI_APPLICATION = 'local_settings.wsgi.application'

# Allow all hosts
ALLOWED_HOSTS = ['*']

# Specify what kind of user contributions an admin can allow for a project.
#   true - All users (including anonymous users) can contribute
#   auth - Only registered users can contribute.
#   false - Only users of the contributors group can contribute
ALLOWED_CONTRIBUTORS = ("true", "auth", "false")

# Allows access to settings within templates.
TEMPLATES[0]['OPTIONS']['context_processors'][:0] = ['geokey.context_processors.allowed_contributors']
