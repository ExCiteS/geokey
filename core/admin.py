from django.conf.urls import patterns, url

from projects import views as project_views

import views as login_views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        login_views.Index.as_view(),
        name='admin:index'),
    url(
        r'^projects/(?P<project_id>[0-9]+)$',
        project_views.ProjectAdminDetail.as_view(),
        name='admin:project'),
)
