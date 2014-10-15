import os

from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.db.models.loading import get_model

from model_utils.managers import InheritanceManager
from django_hstore import hstore, query

from projects.models import Project

from .base import OBSERVATION_STATUS, COMMENT_STATUS


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
    def get_query_set(self):
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
        return self.get_query_set().get_list(project)

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


class ObservationManager(hstore.HStoreManager):
    """
    Manager for Observation Model
    """
    def get_query_set(self):
        """
        Returns all observations excluding those with status `deleted`
        """
        return ObservationQuerySet(self.model).prefetch_related(
            'location', 'observationtype', 'creator', 'updator').exclude(
            status=OBSERVATION_STATUS.deleted)

    def for_moderator(self, user):
        return self.get_query_set().for_moderator(user)

    def for_viewer(self, user):
        return self.get_query_set().for_viewer(user)


class CommentManager(models.Manager):
    """
    Manager for Comment model
    """
    def get_query_set(self):
        """
        Returns all comments excluding those with status `deleted`
        """
        return super(CommentManager, self).get_query_set().exclude(
            status=COMMENT_STATUS.deleted)


class MediaFileManager(InheritanceManager):
    """
    Manger for `MediaFile` model
    """
    def get_query_set(self):
        """
        Returns the subclasses of the MediaFiles. Needed to get access to the 
        actual instances when searching all files of a contribution.
        """
        return super(MediaFileManager, self).get_query_set().select_subclasses()

    def create(self, the_file=None, *args, **kwargs):
        """
        Create a new file. Selects the class by examining the file name
        extension.
        """
        name = kwargs.get('name')
        description = kwargs.get('description')
        creator = kwargs.get('creator')
        contribution = kwargs.get('contribution')

        filename, extension = os.path.splitext(the_file.name)

        if extension in ('.png', '.jpeg', '.jpg', '.gif'):
            ImageFile = get_model('contributions', 'ImageFile')
            return ImageFile.objects.create(
                name=name,
                description=description,
                creator=creator,
                contribution=contribution,
                image=the_file
            )
        else:
            raise TypeError('Files of type %s are currently not supported.'
                            % extension)
