from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User

from opencomap.apps.ajaxapi import views
from opencomap.apps.backend.serializers import serialize_fields
from opencomap.apps.backend.models import *

serialize_fields(User, ['id', 'username', 'first_name', 'last_name', 'email'])

urlpatterns = patterns('',
    url(r'^projects/(?P<project_id>\d+)$', views.projects.updateProject, name='project_update'),
    url(r'^projects/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)$', views.projects.addUserToGroup, name='project_addUserToGroup'),
    url(r'^projects/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)/users/(?P<user_id>\d+)$', views.projects.removeUserFromGroup, name='project_remmoveUserFromGroup'),
)