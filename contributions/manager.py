from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from django_hstore import hstore

from projects.models import Project

from .base import OBSERVATION_STATUS, COMMENT_STATUS


class LocationQuerySet(models.query.QuerySet):
    def get_list(self, project):
        return self.filter(
            Q(private=False) |
            Q(private_for_project=project)
        )


class LocationManager(models.GeoManager):
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
    def get_query_set(self):
        return super(ObservationManager, self).get_query_set().exclude(
            status=OBSERVATION_STATUS.deleted)

    def as_editor(self, user, project_id, observation_id):
        project = Project.objects.get_single(user, project_id)
        observation = project.observations.get(pk=observation_id)
        if (observation.creator == user or project.is_admin(user)):
            return observation
        else:
            raise PermissionDenied('You are not allowed to update this'
                                   'observation')


class CommentManager(hstore.HStoreManager):
    def get_query_set(self):
        return super(CommentManager, self).get_query_set().exclude(
            status=COMMENT_STATUS.deleted)
