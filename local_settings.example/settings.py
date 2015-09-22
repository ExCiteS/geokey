from geokey.core.settings.dev import *

# Default email, used for automated correspondence
# https://docs.djangoproject.com/en/1.8/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = 'sender@example.com'

# django-allauth setting, Determines the e-mail verification method during
# signup.
# see: http://django-allauth.readthedocs.org/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Database settings
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geokey',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Your server's secret key
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Set this to true, if you want to enable video upload. Make sure you set the
# Youtube settings
ENABLE_VIDEO = False

# Youtube account settings. Need to be set if you enable video uploads.
# Follow the guide to obtain the credentials: https://developers.google.com/youtube/registering_an_application
YOUTUBE_AUTH_EMAIL = 'your-email@example.com'
YOUTUBE_AUTH_PASSWORD = 'password'
YOUTUBE_DEVELOPER_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
YOUTUBE_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'

# Adds django packages to default INSTALLED_APPS, use it to register GeoKey
# extensions
INSTALLED_APPS += (

)

# Python path to WSGI application, used by Django's build in server
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#wsgi-application
WSGI_APPLICATION = 'local_settings.wsgi.application'

# Python path to the root URL configuration
# see: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-ROOT_URLCONF
ROOT_URLCONF = 'local_settings.urls'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

MEDIA_ROOT = normpath(join(dirname(dirname(abspath(__file__))), 'assets'))
MEDIA_URL = '/assets/'
