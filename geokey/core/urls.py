"""Core URLs."""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


urlpatterns = [
    url(
        r'^oauth2/',
        include('oauth2_provider.urls', namespace='oauth2_provider')
    ),
    url(
        r'^admin/',
        include('geokey.core.url.admin', namespace='admin')
    ),
    url(
        r'^admin/account/',
        include('allauth.urls')
    ),
    url(
        r'^ajax/',
        include('geokey.core.url.ajax', namespace='ajax')
    ),
    url(
        r'^api/',
        include('geokey.core.url.api', namespace='api')
    ),
    url(
        r'^',
        include('geokey.extensions.urls')
    ),
    url(
        r'^$',
        RedirectView.as_view(url='/admin/', permanent=True)
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [
        url(r'^debug-toolbar/', include(debug_toolbar.urls)),
    ]
