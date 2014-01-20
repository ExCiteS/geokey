from opencomap.apps.backend.models.choice import STATUS_TYPES
from django.core.exceptions import ValidationError

def check_status(func):
	ACCEPTED_STATUS = (
		STATUS_TYPES['ACTIVE'], 
		STATUS_TYPES['INACTIVE']
	)

	def wrapped(*args, **kwargs):
		status = kwargs.get('status')
		if ((status is None) or (status in ACCEPTED_STATUS)):
			return func(*args, **kwargs)
		else:
			raise ValidationError('The status provided is invalid. Accepted values are ACTIVE or INACTIVE')
			
	return wrapped