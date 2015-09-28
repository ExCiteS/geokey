from django.conf.urls import patterns, url

from geokey.projects import views as project_views
from geokey.categories import views as category_views
from geokey.users import views as login_views
from geokey.applications import views as app_views
from geokey.superusertools import views as superuser
from geokey.subsets import views as subsets


urlpatterns = patterns(
    '',
    url(r'^$', login_views.Index.as_view(), name='index'),
    url(r'^dashboard/$', login_views.Dashboard.as_view(), name='dashboard'),

    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/new/$',
        project_views.ProjectCreate.as_view(),
        name='project_create'),
    url(
        r'^projects/involved/$',
        project_views.ProjectsInvolved.as_view(),
        name='projects_involved'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.ProjectOverview.as_view(),
        name='project_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/geographic-extent/$',
        project_views.ProjectExtend.as_view(),
        name='project_extend'),
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
        r'^projects/(?P<project_id>[0-9]+)/usergroups/$',
        login_views.UserGroupList.as_view(),
        name='usergroup_list'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/new/$',
        login_views.UserGroupCreate.as_view(),
        name='usergroup_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/$',
        login_views.UserGroupOverview.as_view(),
        name='usergroup_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/administrators/$',
        login_views.AdministratorsOverview.as_view(),
        name='admins_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/permissions/$',
        login_views.UserGroupPermissions.as_view(),
        name='usergroup_permissions'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/settings/$',
        login_views.UserGroupSettings.as_view(),
        name='usergroup_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/delete/$',
        login_views.UserGroupDelete.as_view(),
        name='usergroup_delete'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/data/$',
        login_views.UserGroupData.as_view(),
        name='usergroup_data'),

    # ###########################
    # CATEGORIES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/$',
        category_views.CategoryList.as_view(),
        name='category_list'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/new/$',
        category_views.CategoryCreate.as_view(),
        name='category_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        category_views.CategoryOverview.as_view(),
        name='category_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/display/$',
        category_views.CategoryDisplay.as_view(),
        name='category_display'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/settings/$',
        category_views.CategorySettings.as_view(),
        name='category_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/delete/$',
        category_views.CategoryDelete.as_view(),
        name='category_delete'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/new/$',
        category_views.FieldCreate.as_view(),
        name='category_field_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/$',
        category_views.FieldSettings.as_view(),
        name='category_field_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/delete/$',
        category_views.FieldDelete.as_view(),
        name='category_field_delete'),

    # ###########################
    # SUBSETS
    # ###########################
    url(r'^projects/(?P<project_id>[0-9]+)/subsets/$',
        subsets.SubsetOverview.as_view(),
        name='subset_list'),
    url(r'^projects/(?P<project_id>[0-9]+)/subsets/new/$',
        subsets.SubsetCreate.as_view(),
        name='subset_create'),
    url(r'^projects/(?P<project_id>[0-9]+)/subsets/(?P<subset_id>[0-9]+)/$',
        subsets.SubsetSettings.as_view(),
        name='subset_settings'),
    url(r'^projects/(?P<project_id>[0-9]+)/subsets/(?P<subset_id>[0-9]+)/data/$',
        subsets.SubsetData.as_view(),
        name='subset_data'),
    url(r'^projects/(?P<project_id>[0-9]+)/subsets/(?P<subset_id>[0-9]+)/delete/$',
        subsets.SubsetDelete.as_view(),
        name='subset_delete'),

    # ###########################
    # APPS
    # ###########################
    url(
        r'^apps/$',
        app_views.ApplicationOverview.as_view(),
        name='app_overview'),
    url(
        r'^apps/connected/$',
        app_views.ApplicationConnected.as_view(),
        name='app_connected'),
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
    url(
        r'^apps/(?P<app_id>[0-9]+)/disconnect/$',
        app_views.ApplicationDisconnect.as_view(),
        name='app_disconnect'),

    # ###########################
    # USERS
    # ###########################
    url(r'^profile/$',
        login_views.UserProfile.as_view(),
        name="userprofile"),

    # ###########################
    # SUPER-USER TOOLS
    # ###########################
    url(r'^superuser-tools/$',
        superuser.PlatformSettings.as_view(),
        name="superuser_index"),
    url(r'^superuser-tools/projects/$',
        superuser.ProjectsList.as_view(),
        name="superuser_projects"),
    url(r'^superuser-tools/manage-superusers/$',
        superuser.ManageSuperUsers.as_view(),
        name="superuser_manage_users"),
    url(r'^superuser-tools/manage-inactive-users/$',
        superuser.ManageInactiveUsers.as_view(),
        name="superuser_manage_inactiveusers"),
)
