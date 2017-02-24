"""Models for subsets."""

from django.conf import settings
from django.db import models

from django_pgjson.fields import JsonBField
from simple_history.models import HistoricalRecords


from geokey.core.mixins import FilterMixin


class Subset(FilterMixin, models.Model):
    """Stores a single subset."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('projects.Project', related_name='subsets')
    filters = JsonBField(blank=True, null=True)
    where_clause = models.TextField(blank=True, null=True)
    history = HistoricalRecords()
