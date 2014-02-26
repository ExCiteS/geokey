from django.conf.urls import patterns, url

from projects import views as project_views

import views as login_views


urlpatterns = patterns(
    '',
    url(r'^$', login_views.Index.as_view(), name='index'),
    url(r'^login$', login_views.Login.as_view(), name='login'),
    url(r'^logout$', login_views.Logout.as_view(), name='logout'),
    url(r'^signup$', login_views.Signup.as_view(), name='signup'),
    url(r'^dashboard$', login_views.Dashboard.as_view(), name='dashboard'),
    url(
        r'^projects/(?P<project_id>[0-9]+)$',
        project_views.ProjectAdminDetail.as_view(),
        name='admin:project'),
)
