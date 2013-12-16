from django.conf.urls import patterns, include, url

from opencomap.apps.admin import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.signin, name='login'),
    url(r'^logout$', views.signout, name='logout'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^signup$', views.signup, name='signup'),
)