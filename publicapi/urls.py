from django.conf.urls import patterns, include, url

import views


urlpatterns = patterns('',
    url(r'^projects$', views.projects.project_list, name='api_project_list'),
    url(r'^projects/(?P<project_id>\d+)$', views.project_single, name='api_project_single'),

    url(r'^projects/(?P<project_id>\d+)/featuretypes$', views.featuretypes.featuretype_list, name='api_project_featuretype_list'),
)