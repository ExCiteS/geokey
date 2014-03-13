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
)
