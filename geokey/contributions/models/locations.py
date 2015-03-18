from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis

from ..base import LOCATION_STATUS
from ..manager import LocationManager


class Location(models.Model):
    """
    Represents a location to which an arbitrary number of observations can be
    attached.
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    geometry = gis.GeometryField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    version = models.IntegerField(default=1)
    private = models.BooleanField(default=False)
    private_for_project = models.ForeignKey('projects.Project', null=True)
    status = models.CharField(
        choices=LOCATION_STATUS,
        default=LOCATION_STATUS.active,
        max_length=20
    )

    objects = LocationManager()

    class Meta:
        app_label = 'contributions'
