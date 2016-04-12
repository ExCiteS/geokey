"""URLs for extensions."""

from os.path import dirname, isfile, join

from django.conf.urls import url, include

from geokey.extensions.base import extensions


urlpatterns = []

for extension in extensions:
    if isfile(join(dirname(__import__(extension).__file__), 'urls.py')):
        urls = '%s.urls' % extension
        urlpatterns.append(url(r'^', include(urls, namespace=extension)))
