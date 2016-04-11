"""Admin URLs."""

from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from geokey.projects import views as project_views
from geokey.categories import views as category_views
from geokey.users import views as login_views
from geokey.applications import views as app_views
from geokey.superusertools import views as superusertools
from geokey.subsets import views as subsets


urlpatterns = [
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
        r'^projects/(?P<project_id>[0-9]+)/geographicextent/$',
        project_views.ProjectGeographicExtent.as_view(),
        name='project_geographicextent'),
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
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/$',
        login_views.UserGroupList.as_view(),
        name='usergroup_list'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/new/$',
        login_views.UserGroupCreate.as_view(),
        name='usergroup_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/$',
        login_views.UserGroupOverview.as_view(),
        name='usergroup_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/administrators/$',
        login_views.AdministratorsOverview.as_view(),
        name='admins_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/permissions/$',
        login_views.UserGroupPermissions.as_view(),
        name='usergroup_permissions'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/settings/$',
        login_views.UserGroupSettings.as_view(),
        name='usergroup_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/delete/$',
        login_views.UserGroupDelete.as_view(),
        name='usergroup_delete'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/data/$',
        login_views.UserGroupData.as_view(),
        name='usergroup_data'),

    # ###########################
    # CATEGORIES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/$',
        category_views.CategoryList.as_view(),
        name='category_list'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/new/$',
        category_views.CategoryCreate.as_view(),
        name='category_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/$',
        category_views.CategoryOverview.as_view(),
        name='category_overview'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/display/$',
        category_views.CategoryDisplay.as_view(),
        name='category_display'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/settings/$',
        category_views.CategorySettings.as_view(),
        name='category_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/delete/$',
        category_views.CategoryDelete.as_view(),
        name='category_delete'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/new/$',
        category_views.FieldCreate.as_view(),
        name='category_field_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/(?P<field_id>[0-9]+)/$',
        category_views.FieldSettings.as_view(),
        name='category_field_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/(?P<field_id>[0-9]+)/delete/$',
        category_views.FieldDelete.as_view(),
        name='category_field_delete'),

    # ###########################
    # SUBSETS
    # ###########################
    url(r'^projects/(?P<project_id>[0-9]+)/'
        r'subsets/$',
        subsets.SubsetList.as_view(),
        name='subset_list'),
    url(r'^projects/(?P<project_id>[0-9]+)/'
        r'subsets/new/$',
        subsets.SubsetCreate.as_view(),
        name='subset_create'),
    url(r'^projects/(?P<project_id>[0-9]+)/'
        r'subsets/(?P<subset_id>[0-9]+)/$',
        subsets.SubsetSettings.as_view(),
        name='subset_settings'),
    url(r'^projects/(?P<project_id>[0-9]+)/'
        r'subsets/(?P<subset_id>[0-9]+)/data/$',
        subsets.SubsetData.as_view(),
        name='subset_data'),
    url(r'^projects/(?P<project_id>[0-9]+)/'
        r'subsets/(?P<subset_id>[0-9]+)/delete/$',
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
    # SUPERUSER TOOLS
    # ###########################
    url(r'^superusertools/$',
        RedirectView.as_view(
            url=reverse_lazy('admin:superusertools_manage_superusers'),
            permanent=False),
        name='superusertools_index'),
    url(r'^superusertools/manage-superusers/$',
        superusertools.ManageSuperusers.as_view(),
        name='superusertools_manage_superusers'),
    url(r'^superusertools/manage-inactive-users/$',
        superusertools.ManageInactiveUsers.as_view(),
        name='superusertools_manage_inactive_users'),
    url(r'^superusertools/manage-projects/$',
        superusertools.ManageProjects.as_view(),
        name='superusertools_manage_projects'),
    url(r'^superuser-tools/platform-settings/$',
        superusertools.PlatformSettings.as_view(),
        name='superusertools_platform_settings'),
]
