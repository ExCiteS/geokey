"""Ajax API URLs."""

from django.conf.urls import url

from geokey.projects import views as project_views
from geokey.categories import views as category_views
from geokey.users import views as user_views
from geokey.superusertools import views as superusertools


urlpatterns = [
    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.ProjectUpdate.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'admins/$',
        project_views.ProjectAdmins.as_view(),
        name='project_admins'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'admins/(?P<user_id>[0-9]+)/$',
        project_views.ProjectAdminsUser.as_view(),
        name='project_admins_user'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/$',
        user_views.UserGroup.as_view(),
        name='usergroup'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'usergroups/(?P<usergroup_id>[0-9]+)/'
        r'users/$',
        user_views.UserGroupUsers.as_view(),
        name='usergroup_users'),

    # ###########################
    # CATEGORIES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/$',
        category_views.CategoryUpdate.as_view(),
        name='category'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/re-order/$',
        project_views.CategoriesReorderView.as_view(),
        name='categories_reorder'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/(?P<field_id>[0-9]+)/$',
        category_views.FieldUpdate.as_view(),
        name='category_field'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/(?P<field_id>[0-9]+)/'
        r'lookupvalues/$',
        category_views.FieldLookups.as_view(),
        name='category_lookupvalues'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/(?P<field_id>[0-9]+)/'
        r'lookupvalues/(?P<value_id>[0-9]+)/$',
        category_views.FieldLookupsUpdate.as_view(),
        name='category_lookupvalues_detail'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/'
        r'fields/re-order/$',
        category_views.FieldsReorderView.as_view(),
        name='category_fields_reorder'),

    # ###########################
    # USER
    # ###########################
    url(r'^users/$', user_views.QueryUsers.as_view(), name='users_users'),

    # ###########################
    # SUPERUSER TOOLS
    # ###########################
    url(r'^superusertools/$',
        superusertools.SuperusersAjaxView.as_view(),
        name='superusertools_superusers'),
    url(r'^superusertools/(?P<user_id>[0-9]+)/$',
        superusertools.SingleSuperuserAjaxView.as_view(),
        name='superusertools_single_superuser'),
]
