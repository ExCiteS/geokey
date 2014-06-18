from .contrib import *

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

AUTH_USER_MODEL = 'users.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'communitymaps',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '[YOUR DB USERNAME]',
        'PASSWORD': '[YOUR DB USERNAME]',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}


INSTALLED_APPS += (
    'projects',
    'observationtypes',
    'contributions',
    'dataviews',
    'users',
    'applications'
)
