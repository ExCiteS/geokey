from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^projects/(?P<project_id>\d+)$', views.projects.update, name='project_update'),
    url(r'^projects/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)/users$', views.projects.add_user_to_group, name='project_addUserToGroup'),
    url(r'^projects/(?P<project_id>\d+)/usergroups/(?P<group_id>\d+)/users/(?P<user_id>\d+)$', views.projects.remove_user_from_group, name='project_remmoveUserFromGroup'),

    url(r'^projects/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)$', views.featuretypes.update, name='featuretype_update'),
    url(r'^projects/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/(?P<field_id>\d+)$', views.featuretypes.update_field, name='featuretype_field_update'),
    url(r'^projects/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/(?P<field_id>\d+)/lookupvalues$', views.featuretypes.add_lookup_value, name='featuretype_field_addlookup'),
    url(r'^projects/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/(?P<field_id>\d+)/lookupvalues/(?P<lookup_id>\d+)$', views.featuretypes.remove_lookup_value, name='featuretype_field_removelookup'),

    url(r'^projects/(?P<project_id>\d+)/views/(?P<view_id>\d+)$', views.views.update, name='view_update'),
    url(r'^projects/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/(?P<group_id>\d+)$', views.views.update_group, name='view_update_group'),
    url(r'^projects/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/(?P<group_id>\d+)/users$', views.views.add_user_to_group, name='view_addUserToGroup'),
    url(r'^projects/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/(?P<group_id>\d+)/users/(?P<user_id>\d+)$', views.views.remove_user_from_group, name='view_addUserToGroup'),

    url(r'^users$', views.users.query_users, name='users_list'),
)