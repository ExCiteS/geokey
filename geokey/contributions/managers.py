"""Managers for contributions."""

import os
import re

import magic
from django.core.files import File
from pytz import utc
from datetime import datetime

from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.template.defaultfilters import slugify

from model_utils.managers import InheritanceManager

from geokey.core.exceptions import FileTypeError, InputError
from geokey.projects.models import Project

from .base import (
    OBSERVATION_STATUS, COMMENT_STATUS, MEDIA_STATUS, ACCEPTED_FILE_TYPES,
    ACCEPTED_AUDIO_TYPES, ACCEPTED_VIDEO_TYPES, ACCEPTED_IMAGE_TYPES, ACCEPTED_DOC_TYPES)

from .utils import (
    get_args,
    get_authenticated_service,
    initialize_upload
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

        If the user is anonymous, it returns only contributions that haven't
        expired yet with status `active` or `review`.

        If the user is not anonymous, it returns only contributions with status
        `active` or `review` as well as `pending` when the given user is
        creator of those contributions.

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
            return self.exclude(
                Q(expiry_field__isnull=False),
                Q(expiry_field__lte=datetime.utcnow().replace(tzinfo=utc)),
            ).exclude(status__in=['draft', 'pending'])
        else:
            return self.for_moderator(user).exclude(
                ~Q(creator=user),
                Q(expiry_field__isnull=False),
                Q(expiry_field__lte=datetime.utcnow().replace(tzinfo=utc)),
            ).exclude(~Q(creator=user), status='pending')

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

    def get_by_bbox(self, bbox):
        """
        Returns a subset of the queryset containing observations where the
        geometry of the location is inside the the passed bbox.

        Parameters
        ----------
        bbox : str
            Str that provides the xmin,ymin,xmax,ymax

        Return
        ------
        django.db.models.Queryset
            List of search results matching the query
        """

        if bbox:
            try:
                # created bbox to Polygon
                from django.contrib.gis.geos import Polygon
                bbox = bbox.split(',')  # Split by ','
                geom_bbox = Polygon.from_bbox(bbox)
                # Filtering observations where
                return self.filter(location__geometry__bboverlaps=geom_bbox)
            except Exception as e:
                raise InputError(str(e) + '. Please, check the coordinates'
                                          ' you attached to bbox parameters, they should follow'
                                          'the OSGeo standards (e.g:bbox=xmin,ymin,xmax,ymax).')


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

    @staticmethod
    def _get_file_id(the_file):
        file_identification = magic.from_buffer(the_file.read(1024))
        # Ensure the next file read starts from the start.
        the_file.seek(0)
        return file_identification

    @staticmethod
    def _get_file_id_data(the_file):
        file_id = MediaFileManager._get_file_id(the_file)
        for id_info, extension in ACCEPTED_FILE_TYPES:
            # Stops at the first match.
            if id_info in file_id:
                return id_info, extension
        return 'Unknown', ''

    @staticmethod
    def _get_file_content_data(a_file):
        content_type = a_file.content_type.split('/')
        id_info, extn = MediaFileManager._get_file_id_data(a_file)
        # Only adjust the content type when no file extension exists.
        if '.' not in a_file.name:
            if (id_info, extn) in ACCEPTED_AUDIO_TYPES:
                content_type[0] = 'audio'
            elif (id_info, extn) in ACCEPTED_VIDEO_TYPES:
                content_type[0] = 'video'
            elif (id_info, extn) in ACCEPTED_IMAGE_TYPES:
                content_type[0] = 'image'
            elif (id_info, extn) in ACCEPTED_DOC_TYPES:
                content_type[0] = 'application'

        if extn == 'aac' and id_info == 'AAC':
            content_type = ('audio', 'aac')

        return content_type, id_info

    @staticmethod
    def _normalise_filename(name):
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

    def _create_document_file(self, name, description, creator, contribution,
                              the_file):
        """
        Creates an DocumentFile and returns the instance.

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
        geokey.contributions.models.DocumentFile
            File created
        """
        from geokey.contributions.models import DocumentFile

        filename, extension = os.path.splitext(the_file.name)
        filename = self._normalise_filename(filename)
        the_file.name = filename[:FILE_NAME_TRUNC] + extension

        return DocumentFile.objects.create(
            name=name,
            description=description,
            creator=creator,
            contribution=contribution,
            document=the_file
        )

    def _create_audio_file(self, name, description, creator, contribution,
                           the_file, content_type):
        """
        Creates an AudioFile and returns the instance.

        All files that are not mp3 get converted using avconv.

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

        converted_file = None

        # Convert using avconv
        if content_type[1] != 'mp3':
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
                r"Stream #\d*\.\d*.*:\s*Video",
                re.MULTILINE
            )

            # Using error because output file is not specified
            if not video_stream.search(error.decode()):
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

        filename, extension = os.path.splitext(the_file.name)
        filename = self._normalise_filename(filename)
        the_file.name = filename[:FILE_NAME_TRUNC] + extension

        audio_file = AudioFile.objects.create(
            name=name,
            description=description,
            creator=creator,
            contribution=contribution,
            audio=the_file
        )

        if converted_file is not None and os.path.isfile(converted_file):
            os.remove(converted_file)

        return audio_file

    @staticmethod
    def _upload_to_youtube(name, path):
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

        youtube = get_authenticated_service()
        args = get_args(name, path)
        video_id = initialize_upload(youtube, args)

        return video_id, 'swf_wtf'

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
        an ImageFile, DocumentFile, VideoFile or AudioFile.

        Parameters
        ----------
        the_file : django.core.files.File
            The file object uploaded by the user

        Returns
        -------
        geokey.contributions.models.ImageFile or
        geokey.contributions.models.DocumentFile or
        geokey.contributions.models.VideoFile or
        geokey.contributions.models.AudioFile
            File created

        Raises
        ------
        FileTypeError
            if the file type is not supported, e.g. DOCs or HTMLs
        """
        name = kwargs.get('name')
        description = kwargs.get('description')
        creator = kwargs.get('creator')
        contribution = kwargs.get('contribution')
        content_type, id_info = MediaFileManager._get_file_content_data(the_file)
        file_type_accepted = any(i[0] in id_info for i in ACCEPTED_FILE_TYPES)
        if content_type[0] == 'image' and file_type_accepted:
            return self._create_image_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )
        elif content_type[0] == 'application' and file_type_accepted:
            return self._create_document_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )
        elif content_type[0] == 'video' and settings.ENABLE_VIDEO and file_type_accepted:
            return self._create_video_file(
                name,
                description,
                creator,
                contribution,
                the_file
            )
        elif content_type[0] in ['audio', 'video'] and file_type_accepted:
            return self._create_audio_file(
                name=name,
                description=description,
                creator=creator,
                contribution=contribution,
                the_file=the_file,
                content_type=content_type
            )
        else:
            raise FileTypeError(
                'Files of type {} ({}) are currently not supported.'.format(id_info, name))
