from django.contrib.gis.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ValidationError

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
    def create(self, **kwargs):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
        observationtype = kwargs.get('observationtype')
        data = kwargs.get('data')

        valid = True
        for field in observationtype.fields.all():
            if not field.validate_input(data.get(field.key)):
                valid = False

        if valid:
            return super(ObservationManager, self).create(**kwargs)
        else:
            raise ValidationError('One or more fields did not validate. The '
                                  'contribution has not been save to the '
                                  'database')

    def get_query_set(self):
        return super(ObservationManager, self).get_query_set().exclude(
            status=OBSERVATION_STATUS.deleted)


class CommentManager(hstore.HStoreManager):
    def get_query_set(self):
        return super(CommentManager, self).get_query_set().exclude(
            status=COMMENT_STATUS.deleted)
