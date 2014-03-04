from django.conf.urls import patterns, url

from projects import views as project_views
from observationtypes import views as observationtypes_views
from users import views as user_views

urlpatterns = patterns(
    '',
    url(
        r'^projects/(?P<project_id>[0-9]+)$',
        project_views.ProjectApiDetail.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users$',
        project_views.ProjectApiUserGroup.as_view(),
        name='project_usergroup'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/(?P<user_id>[0-9]+)$',
        project_views.ProjectApiUserGroupUser.as_view(),
        name='project_usergroup_user'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)$',
        observationtypes_views.ObservationTypeApiDetail.as_view(),
        name='project_observationtype'),
    url(r'^users$', user_views.QueryUsers.as_view(), name='users_users'),
)
