from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User

from opencomap.apps.ajaxapi import views
from opencomap.apps.backend.models import *

urlpatterns = patterns('',
    url(r'^projects/(?P<project_id>\d+)$', views.projects.updateProject, name='project_update'),
    url(r'^projects/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)$', views.projects.addUserToGroup, name='project_addUserToGroup'),
    url(r'^projects/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)/users/(?P<user_id>\d+)$', views.projects.removeUserFromGroup, name='project_remmoveUserFromGroup'),

    url(r'^projects/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)$', views.featuretypes.update, name='featuretype_update'),
)