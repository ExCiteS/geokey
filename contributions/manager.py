from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from django_hstore import hstore

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
            raise PermissionDenied('The location can not be used with this'
                                   'project.')


class ObservationManager(hstore.HStoreManager):
    """
    Manager for Observation Model
    """
    def get_query_set(self):
        """
        Returns all observations excluding those with status `deleted`
        """
        return super(ObservationManager, self).get_query_set().exclude(
            status=OBSERVATION_STATUS.deleted)


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
