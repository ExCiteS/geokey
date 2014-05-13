from django.conf.urls import patterns, url

from projects import views as project_views
from observationtypes import views as observationtype_views
from users import views as login_views
from dataviews import views as view_views
from applications import views as app_views


urlpatterns = patterns(
    '',
    url(r'^$', login_views.Index.as_view(), name='index'),
    url(r'^login$', login_views.Login.as_view(), name='login'),
    url(r'^logout$', login_views.Logout.as_view(), name='logout'),
    url(r'^signup$', login_views.Signup.as_view(), name='signup'),
    url(r'^dashboard$', login_views.Dashboard.as_view(), name='dashboard'),

    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/new/$',
        project_views.ProjectCreate.as_view(),
        name='project_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.ProjectSettings.as_view(),
        name='project_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observations/$',
        project_views.ProjectObservations.as_view(),
        name='project_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observations/(?P<observation_id>[0-9]+)$',
        project_views.ProjectSingleObservation.as_view(),
        name='project_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/mycontributions/',
        project_views.ProjectMyObservations.as_view(),
        name='project_my_observations'),

    # ###########################
    # OBSERVATION TYPES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/new/$',
        observationtype_views.ObservationTypeAdminCreateView.as_view(),
        name='observationtype_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/$',
        observationtype_views.ObservationTypeAdminDetailView.as_view(),
        name='observationtype_detail'),

    # ###########################
    # FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/new/$',
        observationtype_views.FieldAdminCreateView.as_view(),
        name='observationtype_field_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/$',
        observationtype_views.FieldAdminDetailView.as_view(),
        name='observationtype_field_detail'),

    # ###########################
    # VIEWS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/new/$',
        view_views.ViewAdminCreateView.as_view(),
        name='view_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/$',
        view_views.ViewAdminSettingsView.as_view(),
        name='view_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/observations/$',
        view_views.ViewAdminDataView.as_view(),
        name='view_data'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/observations/(?P<observation_id>[0-9]+)$',
        view_views.ViewSingleObservation.as_view(),
        name='view_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/usergroups/new/$',
        view_views.ViewGroupAdminCreateView.as_view(),
        name='view_group_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/$',
        view_views.ViewGroupAdminSettingsView.as_view(),
        name='view_group_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/rules/new/$',
        view_views.RuleCreateView.as_view(),
        name='view_rule_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/rules/(?P<rule_id>[0-9]+)/$',
        view_views.RuleSettingsView.as_view(),
        name='rule_settings'),

    # ###########################
    # APPS
    # ###########################

    url(
        r'^apps/register/$',
        app_views.ApplicationCreate.as_view(),
        name='app_register'),
    url(
        r'^apps/(?P<app_id>[0-9]+)/$',
        app_views.ApplicationSettings.as_view(),
        name='app_settings'),
)
