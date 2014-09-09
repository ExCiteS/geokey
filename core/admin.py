from django.conf.urls import patterns, url, include

from projects import views as project_views
from observationtypes import views as observationtype_views
from users import views as login_views
from dataviews import views as dataviews
from applications import views as app_views

from django.contrib.auth.views import login, logout


urlpatterns = patterns(
    '',
    url(r'^$', login_views.Index.as_view(), name='index'),
    url(r'^dashboard/$', login_views.Dashboard.as_view(), name='dashboard'),

    url(r'^accounts/signup/$', login_views.Signup.as_view(), name='signup'),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout),

    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/new/$',
        project_views.ProjectCreate.as_view(),
        name='project_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.ProjectOverview.as_view(),
        name='project_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/settings/$',
        project_views.ProjectSettings.as_view(),
        name='project_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/delete/$',
        project_views.ProjectDelete.as_view(),
        name='project_delete'),


    # ###########################
    # USER GROUPS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/new/$',
        login_views.UserGroupCreate.as_view(),
        name='usergroup_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/$',
        login_views.UserGroupSettings.as_view(),
        name='usergroup_settings'),

    # ###########################
    # OBSERVATION TYPES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/$',
        observationtype_views.CategoryList.as_view(),
        name='category_list'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/new/$',
        observationtype_views.ObservationTypeCreate.as_view(),
        name='observationtype_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        observationtype_views.CategoryOverview.as_view(),
        name='category_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<observationtype_id>[0-9]+)/settings/$',
        observationtype_views.ObservationTypeSettings.as_view(),
        name='observationtype_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/delete/$',
        observationtype_views.CategoryDelete.as_view(),
        name='category_delete'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<observationtype_id>[0-9]+)/fields/new/$',
        observationtype_views.FieldCreate.as_view(),
        name='observationtype_field_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/$',
        observationtype_views.FieldSettings.as_view(),
        name='observationtype_field_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/delete/$',
        observationtype_views.FieldDelete.as_view(),
        name='category_field_delete'),

    # ###########################
    # VIEWS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/$',
        dataviews.GroupingList.as_view(),
        name='grouping_list'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/new/$',
        dataviews.ViewCreate.as_view(),
        name='view_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/$',
        dataviews.GroupingOverview.as_view(),
        name='grouping_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/permissions/$',
        dataviews.GroupingPermissions.as_view(),
        name='grouping_permissions'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/settings/$',
        dataviews.ViewSettings.as_view(),
        name='view_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/delete/$',
        dataviews.GroupingDelete.as_view(),
        name='grouping_delete'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/filter/new/$',
        dataviews.RuleCreate.as_view(),
        name='view_rule_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/filter/(?P<rule_id>[0-9]+)/$',
        dataviews.RuleSettings.as_view(),
        name='rule_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/filter/(?P<filter_id>[0-9]+)/delete/$',
        dataviews.FilterDelete.as_view(),
        name='filter_delete'),

    # ###########################
    # APPS
    # ###########################

    url(
        r'^apps/$',
        app_views.ApplicationOverview.as_view(),
        name='app_overview'),
    url(
        r'^apps/register/$',
        app_views.ApplicationCreate.as_view(),
        name='app_register'),
    url(
        r'^apps/(?P<app_id>[0-9]+)/$',
        app_views.ApplicationSettings.as_view(),
        name='app_settings'),
    url(
        r'^apps/(?P<app_id>[0-9]+)/delete/$',
        app_views.ApplicationDelete.as_view(),
        name='app_delete'),

    # ###########################
    # USERS
    # ###########################
    url(r'^profile/$',
        login_views.UserProfile.as_view(),
        name="userprofile"),
    url(r'^accounts/password/change/$',
        login_views.ChangePassword.as_view(),
        name="changepassword"),
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/admin/accounts/password/reset/done/'},
        name="password_reset"),
    url(r'^accounts/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/admin/accounts/password/done/'},
        name="password_reset_confirm"),
    url(r'^accounts/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),
)
