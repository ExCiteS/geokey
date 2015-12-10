# Activate the following two lines if you are running GeoKey using
# the test server and plan on uploading files via the API.
# from django.conf import settings
# from django.conf.urls.static import static

from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^', include('geokey.core.urls')),
)  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Activate the following two lines if you are running GeoKey using
# the test server and plan on uploading files via the API.
