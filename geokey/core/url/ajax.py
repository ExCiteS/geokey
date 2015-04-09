from django.conf.urls import patterns, url

from geokey.projects import views as project_views
from geokey.categories import views as category_views
from geokey.datagroupings import views as view_views
from geokey.users import views as user_views
from geokey.superusertools import views as superuser_views

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
        r'^projects/(?P<project_id>[0-9]+)/admins/$',
        project_views.ProjectAdmins.as_view(),
        name='project_admins'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/admins/(?P<user_id>[0-9]+)/$',
        project_views.ProjectAdminsUser.as_view(),
        name='project_admins_user'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/$',
        user_views.UserGroup.as_view(),
        name='usergroup'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/$',
        user_views.UserGroupUsers.as_view(),
        name='usergroup_users'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/(?P<user_id>[0-9]+)/$',
        user_views.UserGroupSingleUser.as_view(),
        name='usergroup_single_user'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/data-groupings/$',
        user_views.UserGroupViews.as_view(),
        name='usergroup_views'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/$',
        user_views.UserGroupSingleView.as_view(),
        name='usergroup_single_view'),

    # ###########################
    # CATEGORIES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        category_views.CategoryUpdate.as_view(),
        name='category'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/re-order/$',
        project_views.CategoriesReorderView.as_view(),
        name='categories_reorder'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/$',
        category_views.FieldUpdate.as_view(),
        name='category_field'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/lookupvalues/$',
        category_views.FieldLookups.as_view(),
        name='category_lookupvalues'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/lookupvalues/(?P<value_id>[0-9]+)/$',
        category_views.FieldLookupsUpdate.as_view(),
        name='category_lookupvalues_detail'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/fields/re-order/$',
        category_views.FieldsReorderView.as_view(),
        name='category_fields_reorder'),

    # ###########################
    # USER
    # ###########################
    url(r'^users/$', user_views.QueryUsers.as_view(), name='users_users'),

    # ###########################
    # SUPER USER
    # ###########################
    url(r'^superusers/$', superuser_views.AddSuperUsersAjaxView.as_view(), name='superusers_adduser'),
    url(r'^superusers/(?P<user_id>[0-9]+)/$', superuser_views.DeleteSuperUsersAjaxView.as_view(), name='superusers_deleteuser'),
)
