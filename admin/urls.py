from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.signin, name='login'),
    url(r'^logout$', views.signout, name='logout'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^signup$', views.signup, name='signup'),

    url(r'^project/new$', views.createProject, name='project_create'),
    url(r'^project/(?P<project_id>\d+)$', views.viewProject, name='project_view'),
    url(r'^project/(?P<project_id>\d+)/settings$', views.editProject, name='project_settings'),

    url(r'^project/(?P<project_id>\d+)/views/new$', views.new, name='view_create'),
    url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)$', views.viewView, name='view_view'),
    url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)/settings$', views.editView, name='view_settings'),
    url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/new$', views.create_usergroup, name='view_create_usergroup'),
    url(r'^project/(?P<project_id>\d+)/views/(?P<view_id>\d+)/usergroups/(?P<group_id>\d+)$', views.view_usergroup, name='view_usergroup_view'),

    url(r'^project/(?P<project_id>\d+)/featuretypes/new$', views.createFeaturetype, name='featuretype_create'),
    url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)$', views.viewFeaturetype, name='featuretype_view'),

    url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/new$', views.createField, name='field_create'),
    url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)/fields/(?P<field_id>\d+)$', views.viewField, name='field_view'),
)
