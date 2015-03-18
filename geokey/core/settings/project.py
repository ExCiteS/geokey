from .dev import *

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
PLATFORM_NAME = 'GeoKey'
DEFAULT_FROM_EMAIL = 'sender@example.com'

YOUTUBE_AUTH_EMAIL = 'your-email@example.com'
YOUTUBE_AUTH_PASSWORD = 'password'
YOUTUBE_DEVELOPER_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
YOUTUBE_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'

SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'geokey',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'django',
        'PASSWORD': 'django123',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}


INSTALLED_APPS += (
    # 'geokey_epicollect',
    # 'geokey_cartodb',
    # 'geokey_communitymaps',
    # 'pantechnicon'
)

AUTH_USER_MODEL = 'users.User'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = normpath(join(SITE_ROOT, 'assets'))
MEDIA_URL = '/assets/'
