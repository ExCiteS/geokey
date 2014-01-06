from django.conf.urls import patterns, include, url
from opencomap.apps.api import views

urlpatterns = patterns('',
    url(r'^ajax/project/(?P<project_id>\d+)/update$', views.updateProject, name='project_update'),
)