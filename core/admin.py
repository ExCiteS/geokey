from django.conf.urls import patterns, url

from projects import views as project_views
from observationtypes import views as observationtype_views
from users import views as login_views


urlpatterns = patterns(
    '',
    url(r'^$', login_views.Index.as_view(), name='index'),
    url(r'^login$', login_views.Login.as_view(), name='login'),
    url(r'^logout$', login_views.Logout.as_view(), name='logout'),
    url(r'^signup$', login_views.Signup.as_view(), name='signup'),
    url(r'^dashboard$', login_views.Dashboard.as_view(), name='dashboard'),

    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/new$',
        project_views.ProjectAdminCreateView.as_view(),
        name='project_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)$',
        project_views.ProjectAdminSettings.as_view(),
        name='project_settings'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data$',
        project_views.ProjectAdminDetailView.as_view(),
        name='project_detail'),

    # ###########################
    # OBSERVATION TYPES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/new$',
        observationtype_views.ObservationTypeAdminCreateView.as_view(),
        name='observationtype_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)$',
        observationtype_views.ObservationTypeAdminDetailView.as_view(),
        name='observationtype_detail'),

    # ###########################
    # FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/new$',
        observationtype_views.FieldAdminCreateView.as_view(),
        name='observationtype_field_create'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)$',
        observationtype_views.FieldAdminDetailView.as_view(),
        name='observationtype_field_detail'),
)
