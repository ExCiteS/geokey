from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^ajax/', include('core.ajax')),
    # url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)
