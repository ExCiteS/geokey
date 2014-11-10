from django.conf.urls import patterns, url

from projects import views as project_views
from categories import views as category_views
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
    url(
        r'^projects/(?P<project_id>[0-9]+)/get-in-touch/$',
        project_views.ProjectContactAdmins.as_view(),
        name='project_contact_admins'),

    # ###########################
    # OBSERVATIONS
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/$',
        contribution_views.ProjectObservations.as_view(),
        name='project_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/search/$',
        contribution_views.ContributionSearchAPIView.as_view(),
        name='contributions_search'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/$',
        contribution_views.ProjectObservationsView.as_view(),
        name='project_all_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/$',
        contribution_views.SingleAllContributionAPIView.as_view(),
        name='project_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/$',
        contribution_views.MyObservations.as_view(),
        name='project_my_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/$',
        contribution_views.SingleMyContributionAPIView.as_view(),
        name='project_my_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/$',
        contribution_views.ViewObservations.as_view(),
        name='single_view'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/$',
        contribution_views.SingleGroupingContributionAPIView.as_view(),
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
        contribution_views.AllContributionsCommentsAPIView.as_view(),
        name='project_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        contribution_views.AllContributionsSingleCommentAPIView.as_view(),
        name='project_single_comment'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/$',
        contribution_views.GroupingContributionsCommentsAPIView.as_view(),
        name='view_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<view_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        contribution_views.GroupingContributionsSingleCommentAPIView.as_view(),
        name='view_single_comment'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/comments/$',
        contribution_views.MyContributionsCommentsAPIView.as_view(),
        name='myobservations_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        contribution_views.MyContributionsSingleCommentAPIView.as_view(),
        name='myobservations_single_comment'),

    # ###########################
    # MEDIA
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<contribution_id>[0-9]+)/media/$',
        contribution_views.AllContributionsMediaAPIView.as_view(),
        name='project_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        contribution_views.AllContributionsSingleMediaApiView.as_view(),
        name='project_single_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<contribution_id>[0-9]+)/media/$',
        contribution_views.MyContributionsMediaApiView.as_view(),
        name='mycontributions_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        contribution_views.MyContributionsSingleMediaApiView.as_view(),
        name='mycontributions_single_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<contribution_id>[0-9]+)/media/$',
        contribution_views.GroupingContributionsMediaApiView.as_view(),
        name='grouping_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        contribution_views.GroupingContributionsSingleMediaApiView.as_view(),
        name='grouping_single_media'),

    # ###########################
    # OBSERVATION TYPES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        category_views.SingleCategory.as_view(),
        name='category'),
)
