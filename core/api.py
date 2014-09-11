from django.conf.urls import patterns, url

from projects import views as project_views
from observationtypes import views as observationtype_views
from contributions import views as contribution_views

urlpatterns = patterns(
    '',
    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/$',
        project_views.Projects.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.SingleProject.as_view(),
        name='project_single'),

    # ###########################
    # OBSERVATIONS
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/$',
        contribution_views.ProjectObservations.as_view(),
        name='project_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/$',
        contribution_views.ProjectObservationsView.as_view(),
        name='project_all_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/$',
        contribution_views.SingleProjectObservation.as_view(),
        name='project_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/$',
        contribution_views.MyObservations.as_view(),
        name='project_my_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/$',
        contribution_views.MySingleObservation.as_view(),
        name='project_my_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/$',
        contribution_views.ViewObservations.as_view(),
        name='single_view'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/$',
        contribution_views.SingleViewObservation.as_view(),
        name='view_single_observation'),

    # ###########################
    # LOCATIONS
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/locations/$',
        contribution_views.Locations.as_view(),
        name='project_locations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/locations/(?P<location_id>[0-9]+)/$',
        contribution_views.SingleLocation.as_view(),
        name='project_single_location'),

    # ###########################
    # COMMENTS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/comments/$',
        contribution_views.ProjectComments.as_view(),
        name='project_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        contribution_views.ProjectSingleComment.as_view(),
        name='project_single_comment'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/$',
        contribution_views.ViewComments.as_view(),
        name='view_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        contribution_views.ViewSingleComment.as_view(),
        name='view_single_comment'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/comments/$',
        contribution_views.MyObservationComments.as_view(),
        name='myobservations_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        contribution_views.MyObservationSingleComment.as_view(),
        name='myobservations_single_comment'),

    # ###########################
    # OBSERVATION TYPES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<observationtype_id>[0-9]+)/$',
        observationtype_views.SingleObservationType.as_view(),
        name='observationtype'),
)
