from django.db import models
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from projects.models import Project

from .base import STATUS


class ObservationTypeManager(models.Manager):
    def all(self, user, project_id):
        """
        Returns all observationtype objects the user is allowed to access
        """
        return Project.objects.get(user, project_id).observationtype_set.filter(
            Q(status=STATUS.active) | Q(project__admins__users=user)
            ).distinct()

    def get_single(self, user, project_id, observationtype_id):
        """
        Returns all a single observationtype. Raises PermissionDenied if user
        is not eligable to access the observationtype.
        """
        observation_type = Project.objects.get(
            user, project_id).observationtype_set.get(pk=observationtype_id)

        if (observation_type.status == STATUS.active or
                observation_type.project.is_admin(user)):
            return observation_type
        else:
            raise PermissionDenied('You are not allowed to access this '
                                   'observationtype')

    def as_admin(self, user, project_id, observationtype_id):
        """
        Returns all a single observationtype for an project admin.
        """
        return Project.objects.as_admin(
            user, project_id
            ).observationtype_set.get(pk=observationtype_id)


class FieldManager(models.Manager):
    use_for_related_fields = True
