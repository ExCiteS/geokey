from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from users.views import ChangePassword


urlpatterns = patterns(
    '',
    url(r'^ajax/', include('core.url.ajax', namespace="ajax")),
    url(r'^admin/', include('core.url.admin', namespace="admin")),
    url(r'^api/', include('core.url.api', namespace="api")),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^admin/account/password/change/', ChangePassword.as_view(), name="account_change_password"),
    url(r'^admin/account/', include('allauth.urls')),
    url(r'^', include('core.url.extensions')),
    url(r'^$', RedirectView.as_view(url='/admin/', permanent=True)),
)

urlpatterns += patterns(
    '',
    (r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
