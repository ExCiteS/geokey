from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.permissions import UserGroup
from opencomap.apps.backend.models.features import Feature
from opencomap.apps.backend.models.choices import STATUS_TYPES

class View(models.Model):

	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	projects = models.ManyToManyField(Project)
	usergroups = models.ManyToManyField(UserGroup)
	features = models.ManyToManyField(Feature)

	class Meta: 
		app_label = 'backend'