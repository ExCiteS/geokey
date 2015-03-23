import os

from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.conf import settings

from model_utils.managers import InheritanceManager
from django_hstore import hstore, query
from django_youtube.api import Api as Youtube, AccessControl

from geokey.core.exceptions import FileTypeError
from geokey.projects.models import Project

from .base import (
    OBSERVATION_STATUS, COMMENT_STATUS, ACCEPTED_IMAGE_FORMATS,
    ACCEPTED_VIDEO_FORMATS, MEDIA_STATUS
)

FILE_NAME_TRUNC = 60 - len(settings.MEDIA_URL)


class LocationQuerySet(models.query.QuerySet):
    """
    Querset manager for Locaion model
    """
    def get_list(self, project):
        """
        Returns a list of all locaation avaiable for that project/
        """
        return self.filter(
            Q(private=False) |
            Q(private_for_project=project)
        )


class LocationManager(models.GeoManager):
    """
    Manager for Location Model
    """
    def get_queryset(self):
        """
        Returns the QuerySet
        """
        return LocationQuerySet(self.model)

    def get_list(self, user, project_id):
        """
        Returns all locations that can be used with the project. Includes all
        non-private locations and locations that a match the
        private_for_project property
        """
        project = Project.objects.as_contributor(user, project_id)
        return self.get_queryset().get_list(project)

    def get_single(self, user, project_id, location_id):
        """
        Returns a single location if the location is not private or if the
        private_for_project property matches the project.
        Raises PermissionDenied if otherwise.
        """
        project = Project.objects.as_contributor(user, project_id)
        location = self.get(pk=location_id)
        if not location.private or location.private_for_project == project:
            return location
        else:
            raise PermissionDenied('The location can not be used with this '
                                   'project.')


class ObservationQuerySet(query.HStoreQuerySet):
    def for_moderator(self, user):
        return self.exclude(~Q(creator=user), status='draft')

    def for_viewer(self, user):
        if user.is_anonymous():
            return self.exclude(status='draft').exclude(status='pending')

        return self.for_moderator(user).exclude(
            ~Q(creator=user), status='pending')

    def search(self, query):
        """
        Returns a subset of the query set filtered by query provided
        """
        regex = r':[^#{5}]*%s' % query
        return self.filter(search_matches__iregex=regex)


class ObservationManager(hstore.HStoreManager):
    """
    Manager for Observation Model
    """
    def get_queryset(self):
        """
        Returns all observations excluding those with status `deleted`
        """
        return ObservationQuerySet(self.model).prefetch_related(
            'location', 'category', 'creator', 'updator').exclude(
            status=OBSERVATION_STATUS.deleted)

    def for_moderator(self, user):
        return self.get_queryset().for_moderator(user)

    def for_viewer(self, user):
        return self.get_queryset().for_viewer(user)


class CommentManager(models.Manager):
    """
    Manager for Comment model
    """
    def get_queryset(self):
        """
        Returns all comments excluding those with status `deleted`
        """
        return super(CommentManager, self).get_queryset().exclude(
            status=COMMENT_STATUS.deleted)


class MediaFileManager(InheritanceManager):
    """
    Manger for `MediaFile` model
    """
    def get_queryset(self):
        """
        Returns the subclasses of the MediaFiles. Needed to get access to the
        actual instances when searching all files of a contribution.
        """
        query_set = super(MediaFileManager, self).get_queryset().exclude(
            status=MEDIA_STATUS.deleted
        )
        return query_set.select_subclasses()

    def _create_image_file(self, name, description, creator, contribution,
                           the_file):
        """
        Creates an ImageFile and returns the instance.
        """
        from geokey.contributions.models import ImageFile

        filename, extension = os.path.splitext(the_file.name)
        the_file.name = filename[:FILE_NAME_TRUNC] + extension

        return ImageFile.objects.create(
            name=name,
            description=description,
            creator=creator,
            contribution=contribution,
            image=the_file
        )

    def _upload_to_youtube(self, name, path):
        """
        Uploads the file from the given path to youtube
        """
        youtube = Youtube()
        youtube.authenticate()
        video_entry = youtube.upload_direct(
            path,
            name,
            access_control=AccessControl.Unlisted
        )

        return video_entry.id.text.split('/')[-1], video_entry.GetSwfUrl()

    def _create_video_file(self, name, description, creator, contribution,
                           the_file):
        """
        Creates a new video file. Uploads the video to Youtube and returns the
        VideoFile instance.
        """
        from geokey.contributions.models import VideoFile
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        filename, extension = os.path.splitext(the_file.name)

        path = default_storage.save(
            'tmp/' + filename + extension,
            ContentFile(the_file.read())
        )
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        video_id, swf_link = self._upload_to_youtube(
            name,
            tmp_file
        )
        os.remove(tmp_file)

        return VideoFile.objects.create(
            name=name,
            description=description,
            creator=creator,
            contribution=contribution,
            video=the_file,
            youtube_id=video_id,
            youtube_link='http://www.youtube.com/embed/' + video_id,
            swf_link=swf_link
        )

    def create(self, the_file=None, **kwargs):
        """
        Create a new file. Selects the class by examining the file name
        extension.
        """
        name = kwargs.get('name')
        description = kwargs.get('description')
        creator = kwargs.get('creator')
        contribution = kwargs.get('contribution')

        content_type = the_file.content_type.split('/')

        if (content_type[0] == 'image' and
                content_type[1] in ACCEPTED_IMAGE_FORMATS):
            return self._create_image_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )

        elif (content_type[0] == 'video' and
                content_type[1] in ACCEPTED_VIDEO_FORMATS):
            return self._create_video_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )
        else:
            raise FileTypeError('Files of type %s are currently not supported.'
                                % the_file.content_type)
