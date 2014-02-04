from django.conf.urls import patterns, include, url
from opencomap.apps.admin import views

urlpatterns = patterns('',
    url(r'^$', views.users.index, name='index'),
    url(r'^login$', views.users.signin, name='login'),
    url(r'^logout$', views.users.signout, name='logout'),
    url(r'^dashboard$', views.users.dashboard, name='dashboard'),
    url(r'^signup$', views.users.signup, name='signup'),

	url(r'^project/new$', views.projects.createProject, name='project_create'),
	url(r'^project/(?P<project_id>\d+)$', views.projects.viewProject, name='project_view'),
	url(r'^project/(?P<project_id>\d+)/settings$', views.projects.editProject, name='project_settings'),

	url(r'^project/(?P<project_id>\d+)/views/new$', views.views.new, name='view_create'),
	url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)$', views.views.viewView, name='view_view'),
	url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)/settings$', views.views.editView, name='view_settings'),
	url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/new$', views.views.create_usergroup, name='view_create_usergroup'),
	url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/(?P<group_id>\d+)$', views.views.view_usergroup, name='view_usergroup_view'),

	url(r'^project/(?P<project_id>\d+)/featuretypes/new$', views.featuretypes.createFeaturetype, name='featuretype_create'),
	url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)$', views.featuretypes.viewFeaturetype, name='featuretype_view'),

	url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/new$', views.featuretypes.createField, name='field_create'),
	url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/(?P<field_id>\d+)$', views.featuretypes.viewField, name='field_view'),
)