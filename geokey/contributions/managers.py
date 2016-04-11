"""Managers for contributions."""

import os
import re

from datetime import datetime

from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.template.defaultfilters import slugify

from model_utils.managers import InheritanceManager
from django_youtube.api import Api as Youtube, AccessControl

from geokey.core.exceptions import FileTypeError
from geokey.projects.models import Project

from .base import (
    OBSERVATION_STATUS, COMMENT_STATUS, ACCEPTED_IMAGE_FORMATS,
    ACCEPTED_AUDIO_FORMATS, ACCEPTED_VIDEO_FORMATS, MEDIA_STATUS
)

FILE_NAME_TRUNC = 60 - len(settings.MEDIA_URL)


class LocationQuerySet(models.query.QuerySet):
    """
    Querset manager for Locaion model
    """
    def get_list(self, project):
        """
        Returns a list of all locations avaiable for that project

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project locations are queried for

        Return
        ------
        django.db.models.Queryset
            All Locations available for the project
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
        Returns the QuerySet. Overwrites the method for specific queryset
        methods

        Returns
        -------
        django.db.models.Queryset
            All Locations
        """
        return LocationQuerySet(self.model)

    def get_list(self, user, project_id):
        """
        Returns all locations that can be used with the project. Includes all
        non-private locations and locations that a match the
        private_for_project property

        Parameters
        ----------
        user : geokey.users.models.User
            User locations are queried for
        project_id : int
            identifies the project in the database

        Returns
        -------
        django.db.models.Queryset
            All locations for user and project
        """
        project = Project.objects.as_contributor(user, project_id)
        return self.get_queryset().get_list(project)

    def get_single(self, user, project_id, location_id):
        """
        Returns a single location if the location is not private or if the
        private_for_project property matches the project.

        Parameters
        ----------
        user : geokey.users.models.User
            User locations are queried for
        project_id : int
            identifies the project in the database
        location_id : int
            identifies the location in the database

        Returns
        -------
        geokey.contributions.models.Location
            The location requested

        Raises
        ------
        PermissionDenied
            if user is not allowed to access project or use the location
        """
        project = Project.objects.as_contributor(user, project_id)
        location = self.get(pk=location_id)
        if not location.private or location.private_for_project == project:
            return location
        else:
            raise PermissionDenied('The location can not be used with this '
                                   'project.')


class ObservationQuerySet(models.query.QuerySet):
    """
    Implements custom queryset methods that are applied in ObservationManager
    """
    def for_moderator(self, user):
        """
        Returns all observations for moderators; That includes all observations
        in a project; except this with status='draft', which where not created
        by the given user.

        Parameters
        ----------
        user : geokey.users.models.User
            User that contributions are filtered for

        Return
        ------
        django.db.models.Queryset
            List of observations for moderators
        """
        return self.exclude(~Q(creator=user), status='draft')

    def for_viewer(self, user):
        """
        Returns all observations for viewer, i.e. users who have no moderation
        permissions on the projects.

        If the user is anonymous, it returns only observations with
        status='active' and status='review'

        If the user is not anonymous, it returns it returns only observations
        with status='active' and status='review' as well as status='pending'
        when the given user is creator of those observation.

        Parameters
        ----------
        user : geokey.users.models.User
            User that contributions are filtered for

        Return
        ------
        django.db.models.Queryset
            List of observations for viewer
        """
        if user.is_anonymous():
            return self.exclude(status='draft').exclude(status='pending')

        return self.for_moderator(user).exclude(
            ~Q(creator=user), status='pending')

    def search(self, query):
        """
        Returns a subset of the queryset containing observations where one of
        the properties matches the given query.

        Parameters
        ----------
        query : str
            Query that needs to matched

        Return
        ------
        django.db.models.Queryset
            List of search results matching the query
        """
        if query:
            cleaned = re.sub(r'[\W_]+', ' ', query)
            terms = cleaned.lower().split()

            if terms:
                queries = []
                for term in terms:
                    term = '%%' + term + '%%'
                    q = "(search_index LIKE '%s')" % term
                    queries.append(q)

                return self.extra(where=[' OR '.join(queries)])

        return self


class ObservationManager(models.Manager):
    """
    Manager for Observation Model
    """
    def get_queryset(self):
        """
        Returns all observations excluding those with status `deleted`

        Return
        ------
        django.db.models.Queryset
            All observations excluding deleted
        """
        return ObservationQuerySet(self.model).prefetch_related(
            'location', 'category', 'creator', 'updator').exclude(
            status=OBSERVATION_STATUS.deleted)

    def for_moderator(self, user):
        """
        Returns all observations for moderators; see
        ObservationQuerySet.for_moderator for more info

        Parameter
        ---------
        user : geokey.users.models.User
            User observations are queried for

        Return
        ------
        django.db.models.Queryset
            All observations for moderators
        """
        return self.get_queryset().for_moderator(user)

    def for_viewer(self, user):
        """
        Returns all observations for viewers; see
        ObservationQuerySet.for_viewer for more info

        Parameter
        ---------
        user : geokey.users.models.User
            User observations are queried for

        Return
        ------
        django.db.models.Queryset
            All observations for viewer
        """
        return self.get_queryset().for_viewer(user)


class CommentManager(models.Manager):
    """
    Manager for Comment model
    """
    def get_queryset(self):
        """
        Returns all comments excluding those with status='deleted'

        Return
        ------
        django.db.models.Queryset
            All comments
        """
        return super(CommentManager, self).get_queryset().exclude(
            status=COMMENT_STATUS.deleted)


class MediaFileManager(InheritanceManager):
    """
    Manger for MediaFile model
    """
    def get_queryset(self):
        """
        Returns the subclasses of the MediaFiles; i.e. ImageFile or VideoFile
        instances are returned rather that MediaFile instances. Excludes
        deleted files.

        Return
        ------
        django.db.models.Queryset
            All media files
        """
        query_set = super(MediaFileManager, self).get_queryset().exclude(
            status=MEDIA_STATUS.deleted
        )
        return query_set.select_subclasses()

    def _normalise_filename(self, name):
        filename = slugify(name)
        if len(filename) < 1:
            filename = 'file_%s' % datetime.now().microsecond

        return filename

    def _create_image_file(self, name, description, creator, contribution,
                           the_file):
        """
        Creates an ImageFile and returns the instance.

        Parameter
        ---------
        name : str
            Name of the file (short caption)
        description : str
            Long-form description (or caption) for the file
        creator : geokey.users.models.User
            User who created the file
        contribution : geokey.contributions.models.Observation
            Observation the file is assigned to
        the_file : django.core.files.File
            The actual file

        Return
        ------
        geokey.contributions.models.ImageFile
            File created
        """
        from geokey.contributions.models import ImageFile

        filename, extension = os.path.splitext(the_file.name)
        filename = self._normalise_filename(filename)
        the_file.name = filename[:FILE_NAME_TRUNC] + extension

        return ImageFile.objects.create(
            name=name,
            description=description,
            creator=creator,
            contribution=contribution,
            image=the_file
        )

    def _create_audio_file(self, name, description, creator, contribution,
                           the_file):
        """
        Creates an AudioFile and returns the instance.

        Parameter
        ---------
        name : str
            Name of the file (short caption)
        description : str
            Long-form description (or caption) for the file
        creator : geokey.users.models.User
            User who created the file
        contribution : geokey.contributions.models.Observation
            Observation the file is assigned to
        the_file : django.core.files.File
            The actual file

        Return
        ------
        geokey.contributions.models.AudioFile
            File created
        """
        from geokey.contributions.models import AudioFile

        filename, extension = os.path.splitext(the_file.name)
        filename = self._normalise_filename(filename)
        the_file.name = filename[:FILE_NAME_TRUNC] + extension

        return AudioFile.objects.create(
            name=name,
            description=description,
            creator=creator,
            contribution=contribution,
            audio=the_file
        )

    def _upload_to_youtube(self, name, path):
        """
        Uploads the file from the given path to youtube

        Parameter
        ---------
        name : str
            Name of the file (short caption)
        path : str
            Path to tempory file

        Return
        ------
        str, str
            Youtube video id, Youtube SWF url
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

        Parameter
        ---------
        name : str
            Name of the file (short caption)
        description : str
            Long-form description (or caption) for the file
        creator : geokey.users.models.User
            User who created the file
        contribution : geokey.contributions.models.Observation
            Observation the file is assigned to
        the_file : django.core.files.File
            The actual file

        Return
        ------
        geokey.contributions.models.VideoFile
            File created
        """
        from geokey.contributions.models import VideoFile
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        filename, extension = os.path.splitext(the_file.name)
        filename = self._normalise_filename(filename)

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
            youtube_link='https://www.youtube.com/embed/' + video_id,
            swf_link=swf_link
        )

    def create(self, the_file=None, **kwargs):
        """
        Create a new file. Evaluates the file's content type and creates either
        an ImageFile, AudioFile or VideoFile.

        3gpp/3gpp2 audio files are converted to mp3 by default using avconv.

        Parameters
        ----------
        the_file : django.core.files.File
            The file object uploaded by the user

        Returns
        -------
        geokey.contributions.models.ImageFile or
        geokey.contributions.models.AudioFile or
        geokey.contributions.models.VideoFile
            File created

        Raises
        ------
        FileTypeError
            if the file type is not supported, e.g. PDFs
        """
        name = kwargs.get('name')
        description = kwargs.get('description')
        creator = kwargs.get('creator')
        contribution = kwargs.get('contribution')

        content_type = the_file.content_type.split('/')
        converted_file = None

        # Using avconv to scan and convert 3gpp/3gpp2 audio files to mp3
        if content_type[1] in ['3gpp', '3gpp2']:
            import time
            import shlex
            import subprocess
            from django.core.files import File
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile

            filename, extension = os.path.splitext(the_file.name)
            filename = self._normalise_filename(filename)

            path = default_storage.save(
                'tmp/' + filename + extension,
                ContentFile(the_file.read())
            )
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)

            cmd = shlex.split('avconv -i %s' % tmp_file)
            pipe = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output, error = pipe.communicate()

            video_stream = re.compile(
                r"Stream #\d*\.\d*.*\:\s*Video",
                re.MULTILINE
            )

            # Using error because output file is not specified
            if not video_stream.search(error):
                content_type[0] = 'audio'

                converted_file = os.path.join(
                    settings.MEDIA_ROOT,
                    'tmp',
                    '%s_%s.mp3' % (filename, int(time.time()))
                )

                cmd = shlex.split(
                    'avconv -nostats -loglevel 0 -y -i %s -c:a libmp3lame -q:a 4 -ar 44100 %s' % (
                        tmp_file,
                        converted_file
                    )
                )
                pipe = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, error = pipe.communicate()

                if not error:
                    the_file = File(open(converted_file, 'rb'))
                    the_file.name = '%s.mp3' % filename

            os.remove(tmp_file)

        if (content_type[0] == 'image' and
                content_type[1] in ACCEPTED_IMAGE_FORMATS):
            return self._create_image_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )
        elif (content_type[0] == 'audio' and
                content_type[1] in ACCEPTED_AUDIO_FORMATS):
            audio_file = self._create_audio_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )

            if converted_file is not None and os.path.isfile(converted_file):
                os.remove(converted_file)

            return audio_file
        elif (content_type[0] == 'video' and
                settings.ENABLE_VIDEO and
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
