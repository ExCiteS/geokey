import os.path
from geokey.core.settings.dev import *

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DEFAULT_FROM_EMAIL = 'sender@example.com'
ACCOUNT_EMAIL_VERIFICATION = 'none'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'geokey',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

YOUTUBE_AUTH_EMAIL = 'your-email@example.com'
YOUTUBE_AUTH_PASSWORD = 'password'
YOUTUBE_DEVELOPER_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
YOUTUBE_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'


INSTALLED_APPS += (
    # 'geokey_epicollect',
    # 'geokey_cartodb',
    # 'geokey_communitymaps',
    # 'pantechnicon'
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = normpath(join(SITE_ROOT, 'assets'))
MEDIA_URL = '/assets/'

WSGI_APPLICATION = 'wsgi.application'

if os.path.exists('urls.py'):
    ROOT_URLCONF = 'urls'
else:
    ROOT_URLCONF = 'geokey.core.urls'
