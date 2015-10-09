from django.conf.urls import url, include

from geokey.extensions.base import extensions


urlpatterns = []

for extension, settings in extensions.iteritems():
    if settings['display_admin']:
        urls = '%s.urls' % extension
        urlpatterns.append(url(r'^', include(urls, namespace=extension)))
