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
        r'^projects/(?P<project_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/$',
        observations.SingleAllContributionAPIView.as_view(),
        name='project_single_observation'),

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
        r'^projects/(?P<project_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/$',
        comments.AllContributionsCommentsAPIView.as_view(),
        name='project_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/(?P<observation_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        comments.AllContributionsSingleCommentAPIView.as_view(),
        name='project_single_comment'),

    # ###########################
    # MEDIA
    # ###########################

    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/(?P<contribution_id>[0-9]+)/media/$',
        media.AllContributionsMediaAPIView.as_view(),
        name='project_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/contributions/(?P<contribution_id>[0-9]+)/media/(?P<file_id>[0-9]+)/$',
        media.AllContributionsSingleMediaApiView.as_view(),
        name='project_single_media'),

    # ###########################
    # CATEGORIES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        category_views.SingleCategory.as_view(),
        name='category'),
)
