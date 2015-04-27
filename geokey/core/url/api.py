from django.conf.urls import patterns, url

from geokey.projects import views as project_views
from geokey.categories import views as category_views

from geokey.contributions.views import observations, comments, locations, media
from geokey.users.views import UserAPIView, ChangePasswordView


urlpatterns = patterns(
    '',
    # ###########################
    # USER
    # ###########################
    url(r'^user/$', UserAPIView.as_view(), name='user_api'),
    url(r'^user/password/change/$', ChangePasswordView.as_view(), name='changepassword'),

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
        observations.ProjectObservations.as_view(),
        name='project_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/search/$',
        observations.ContributionSearchAPIView.as_view(),
        name='contributions_search'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/$',
        observations.ProjectObservationsView.as_view(),
        name='project_all_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/$',
        observations.SingleAllContributionAPIView.as_view(),
        name='project_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/$',
        observations.MyObservations.as_view(),
        name='project_my_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/$',
        observations.SingleMyContributionAPIView.as_view(),
        name='project_my_single_observation'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/$',
        observations.ViewObservations.as_view(),
        name='single_view'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/$',
        observations.SingleGroupingContributionAPIView.as_view(),
        name='view_single_observation'),

    # ###########################
    # LOCATIONS
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/locations/$',
        locations.Locations.as_view(),
        name='project_locations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/locations/(?P<location_id>[0-9]+)/$',
        locations.SingleLocation.as_view(),
        name='project_single_location'),

    # ###########################
    # COMMENTS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/comments/$',
        comments.AllContributionsCommentsAPIView.as_view(),
        name='project_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        comments.AllContributionsSingleCommentAPIView.as_view(),
        name='project_single_comment'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/$',
        comments.GroupingContributionsCommentsAPIView.as_view(),
        name='view_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        comments.GroupingContributionsSingleCommentAPIView.as_view(),
        name='view_single_comment'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/comments/$',
        comments.MyContributionsCommentsAPIView.as_view(),
        name='myobservations_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        comments.MyContributionsSingleCommentAPIView.as_view(),
        name='myobservations_single_comment'),

    # ###########################
    # MEDIA
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<contribution_id>[0-9]+)/media/$',
        media.AllContributionsMediaAPIView.as_view(),
        name='project_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/all-contributions/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        media.AllContributionsSingleMediaApiView.as_view(),
        name='project_single_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<contribution_id>[0-9]+)/media/$',
        media.MyContributionsMediaApiView.as_view(),
        name='mycontributions_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/my-contributions/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        media.MyContributionsSingleMediaApiView.as_view(),
        name='mycontributions_single_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<contribution_id>[0-9]+)/media/$',
        media.GroupingContributionsMediaApiView.as_view(),
        name='grouping_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/data-groupings/(?P<grouping_id>[0-9]+)/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        media.GroupingContributionsSingleMediaApiView.as_view(),
        name='grouping_single_media'),

    # ###########################
    # CATEGORIES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        category_views.SingleCategory.as_view(),
        name='category'),
)
