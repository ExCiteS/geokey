from django.db import models
from opencomap.apps.backend.models.choices import STATUS_TYPES

class QuerySet(models.query.QuerySet):
	"""
	QuerySet for models having a field status. User by ActiveManager.
	"""
	def active(self):
		return self.filter(status=STATUS_TYPES['ACTIVE'])

class Manager(models.Manager):
	"""
	Manager for models having a field status. Is required to render active items only in templates.
	"""
	use_for_related_fields = True

	def get_query_set(self):
		return QuerySet(self.model).exclude(status=STATUS_TYPES['DELETED'])

	def active(self, *args, **kwargs):
		return self.get_query_set().active(*args, **kwargs)