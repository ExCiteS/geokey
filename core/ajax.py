from django.conf.urls import patterns, url

from projects import views as project_views
from observationtypes import views as observationtypes_views
from dataviews import views as view_views
from users import views as user_views
from applications import views as app_views

urlpatterns = patterns(
    '',
    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.ProjectUpdate.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/$',
        project_views.ProjectUserGroup.as_view(),
        name='project_usergroup'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/(?P<user_id>[0-9]+)/$',
        project_views.ProjectUserGroupUser.as_view(),
        name='project_usergroup_user'),

    # ###########################
    # OBSERVATION TYPES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/$',
        observationtypes_views.ObservationTypeUpdate.as_view(),
        name='observationtype'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/$',
        observationtypes_views.FieldUpdate.as_view(),
        name='observationtype_field'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/lookupvalues/$',
        observationtypes_views.FieldLookups.as_view(),
        name='observationtype_lookupvalues'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/lookupvalues/(?P<value_id>[0-9]+)/$',
        observationtypes_views.FieldLookupsUpdate.as_view(),
        name='observationtype_lookupvalues_detail'),

    # ###########################
    # VIEWS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/$',
        view_views.ViewApiDetail.as_view(),
        name='view'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/$',
        view_views.ViewUserGroupApiDetail.as_view(),
        name='view_group'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/$',
        view_views.ViewUserGroupUsersApi.as_view(),
        name='view_group_users'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/(?P<user_id>[0-9]+)/$',
        view_views.ViewUserGroupUsersApiDetail.as_view(),
        name='view_group_users_user'),

    # ###########################
    # OBSERVATIONS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observations/$',
        project_views.ProjectAjaxObservations.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/mycontributions/$',
        project_views.ProjectAjaxMyObservations.as_view(),
        name='project_my_contributions'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/observations/$',
        view_views.ViewApiData.as_view(),
        name='view_data'),

    # ###########################
    # APPS
    # ###########################
    url(
        r'^apps/(?P<app_id>[0-9]+)/$',
        app_views.ApplicationUpdate.as_view(),
        name='app_update'),

    # ###########################
    # USER
    # ###########################
    url(r'^users/$', user_views.QueryUsers.as_view(), name='users_users'),
)
