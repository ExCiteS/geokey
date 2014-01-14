from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User

from opencomap.apps.publicapi import views
from opencomap.apps.backend.serializers import serialize_fields
from opencomap.apps.backend.models import *

serialize_fields(User, ['id', 'username', 'first_name', 'last_name', 'email'])

urlpatterns = patterns('',
    url(r'^projects$', views.projects.listProjects, name='project_list'),
    url(r'^projects/(?P<project_id>\d+)$', views.projects.singleProject, name='project_single'),
)