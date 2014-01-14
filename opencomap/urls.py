from django.conf.urls import patterns, include, url

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^admin/', include('opencomap.apps.admin.urls')),
    url(r'^api/', include('opencomap.apps.publicapi.urls')),
    url(r'^ajax/', include('opencomap.apps.ajaxapi.urls')),
)