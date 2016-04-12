"""Public API URLs."""

from django.conf.urls import url

from geokey.core.views import InfoAPIView

from geokey.projects import views as project_views
from geokey.categories import views as category_views

from geokey.contributions.views import observations, comments, locations, media
from geokey.users.views import UserAPIView, ChangePasswordView


urlpatterns = [
    # ###########################
    # CORE
    # ###########################
    url(
        r'^info/$',
        InfoAPIView.as_view(),
        name='info'),

    # ###########################
    # USERS
    # ###########################
    url(
        r'^user/$',
        UserAPIView.as_view(),
        name='user_api'),
    url(
        r'^user/password/change/$',
        ChangePasswordView.as_view(),
        name='changepassword'),

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
    # CATEGORIES
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/$',
        category_views.SingleCategory.as_view(),
        name='category'),

    # ###########################
    # CONTRIBUTIONS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'contributions/$',
        observations.ProjectObservations.as_view(),
        name='project_observations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'contributions/(?P<observation_id>[0-9]+)/$',
        observations.SingleAllContributionAPIView.as_view(),
        name='project_single_observation'),

    # ###########################
    # LOCATIONS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)'
        r'/locations/$',
        locations.LocationsAPIView.as_view(),
        name='project_locations'),
    url(
        r'^projects/(?P<project_id>[0-9]+)'
        r'/locations/(?P<location_id>[0-9]+)/$',
        locations.SingleLocationAPIView.as_view(),
        name='project_single_location'),

    # ###########################
    # COMMENTS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'contributions/(?P<contribution_id>[0-9]+)/'
        r'comments/$',
        comments.CommentsAPIView.as_view(),
        name='project_comments'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'contributions/(?P<contribution_id>[0-9]+)/'
        r'comments/(?P<comment_id>[0-9]+)/$',
        comments.SingleCommentAPIView.as_view(),
        name='project_single_comment'),

    # ###########################
    # MEDIA
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'contributions/(?P<contribution_id>[0-9]+)/'
        r'media/$',
        media.MediaAPIView.as_view(),
        name='project_media'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/'
        r'contributions/(?P<contribution_id>[0-9]+)/'
        r'media/(?P<file_id>[0-9]+)/$',
        media.SingleMediaAPIView.as_view(),
        name='project_single_media'),
]
