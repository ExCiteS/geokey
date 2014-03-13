from django.conf.urls import patterns, url

from projects import views as project_views

urlpatterns = patterns(
    '',
    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects$',
        project_views.ProjectApiList.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)$',
        project_views.ProjectApiSingle.as_view(),
        name='project_single'),
)
