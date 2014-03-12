from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^ajax/', include('core.ajax', namespace="ajax")),
    url(r'^admin/', include('core.admin', namespace="admin")),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)
