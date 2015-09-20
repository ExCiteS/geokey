from django.conf.urls import url, include

from geokey.extensions.base import extensions


urlpatterns = []

for extension in extensions:
    try:
        urls = '%s.urls' % extension
        __import__(urls)
        urlpatterns.append(url(r'^', include(urls, namespace=extension)))
    except ImportError:
        pass
