from django.conf.urls import patterns, url

from projects import views as project_views
from users import views as user_views

urlpatterns = patterns(
    '',
    url(
        r'^projects/(?P<project_id>[0-9]+)$',
        project_views.ProjectApiDetail.as_view(),
        name='project'),
    url(r'^users$', user_views.QueryUsers.as_view(), name='users_users'),
)
