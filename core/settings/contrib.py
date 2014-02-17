from .base import *

INSTALLED_APPS += (
    'djorm_core',
    'djorm_expressions',
    'djorm_hstore',
    'djorm_hstore.tests',
    'provider',
    'provider.oauth2',
    'south',
)
