from django.db import models
from opencomap.apps.backend.models.choices import STATUS_TYPES

class ActiveQuerySet(models.query.QuerySet):
	"""
	QuerySer for models having a field status. User by ActiveManager.
	"""
	def active(self):
		return self.filter(status=STATUS_TYPES['ACTIVE'])

class ActiveManager(models.Manager):
	"""
	Manager for models having a field status. Is required to render active items only in templates.
	"""
	use_for_related_fields = True

	def get_query_set(self):
		return ActiveQuerySet(self.model)

	def active(self, *args, **kwargs):
		return self.get_query_set().active(*args, **kwargs)