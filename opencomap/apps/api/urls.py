from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User

from opencomap.apps.api import views
from opencomap.apps.api.serializers import serialize_fields



serialize_fields(User, ['username', 'first_name', 'last_name', 'email'])

urlpatterns = patterns('',
    url(r'^ajax/project/(?P<project_id>\d+)$', views.updateProject, name='project_update'),
    url(r'^ajax/project/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)$', views.addUserToGroup, name='project_addUserToGroup'),
    url(r'^ajax/project/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)/users/(?P<user_id>\d+)$', views.removeUserFromGroup, name='project_remmoveUserFromGroup'),
)