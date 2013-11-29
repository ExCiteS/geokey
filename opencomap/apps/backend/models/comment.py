from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.feature import Observation
from opencomap.apps.backend.models.choice import STATUS_TYPES

class Comment(models.Model):
	id = models.AutoField(primary_key=True)
	text = models.TextField()
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	respondsto = models.ForeignKey('Comment')

	class Meta:
		abstract = True

class FeatureComment(Comment):
	feature = models.ForeignKey(Feature)

class ObservationComment(Comment):
	observation = models.ForeignKey(Observation)