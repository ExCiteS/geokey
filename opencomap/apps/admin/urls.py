from django.conf.urls import patterns, include, url

from opencomap.apps.admin import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.signin, name='login'),
    url(r'^logout$', views.signout, name='logout'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^signup$', views.signup, name='signup'),

	url(r'^project/new$', views.createProject, name='project:create'),
	url(r'^project/(?P<project_id>\d+)$', views.viewProject, name='project:view'),
	url(r'^project/(?P<project_id>\d+)/settings$', views.editProject, name='project:settings'),

	url(r'^ajax/project/(?P<project_id>\d+)/update$', views.updateProject, name='project:update'),
)