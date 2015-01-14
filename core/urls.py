from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from users.views import SignupAPIView

urlpatterns = patterns(
    '',
    url(r'^ajax/', include('core.ajax', namespace="ajax")),
    url(r'^admin/', include('core.admin', namespace="admin")),
    url(r'^api/', include('core.api', namespace="api")),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^oauth2/signup/$', SignupAPIView.as_view(), name='sign_up_api'),
    url(r'^$', RedirectView.as_view(url='/admin/', permanent=True)),
)

urlpatterns += patterns('',
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
