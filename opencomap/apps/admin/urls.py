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

	url(r'^project/(?P<project_id>\d+)/featuretypes/new$', views.featuretypes.createFeaturetype, name='featuretype_create'),
	url(r'^project/(?P<project_id>\d+)/featuretypes/(?P<featuretype_id>\d+)$', views.featuretypes.viewFeaturetype, name='featuretype_view'),
)