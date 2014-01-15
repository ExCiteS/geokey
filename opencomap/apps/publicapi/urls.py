from django.conf.urls import patterns, include, url

from opencomap.apps.publicapi import views
from opencomap.apps.backend.models import *

urlpatterns = patterns('',
    url(r'^projects$', views.projects.listProjects, name='project_list'),
    url(r'^projects/(?P<project_id>\d+)$', views.projects.singleProject, name='project_single'),
)