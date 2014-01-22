from opencomap.apps.backend.models.featuretype import LookupValue
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.libs.exceptions import MalformedBody

from decorators import check_admin

@check_admin
def update(user, project_id, featuretype_id, data, project=None):
	featuretype = project.featuretype_set.get(pk=featuretype_id)
	if data.get('description') != None: featuretype.update(description=data.get('description'))
	if data.get('status') != None: featuretype.update(status=data.get('status'))
	return featuretype

@check_admin
def updateField(user, project_id, featuretype_id, field_id, data, project=None):
	field = project.featuretype_set.get(pk=featuretype_id).getField(field_id)
	if data.get('description') != None: field.update(description=data.get('description'))
	if data.get('status') != None: field.update(status=data.get('status'))
	if data.get('required') != None: field.update(required=data.get('required'))
	return field

@check_admin
def addLookupValue(user, project_id, featuretype_id, field_id, data, project=None):
	field = project.featuretype_set.get(pk=featuretype_id).getField(field_id)
	if data.get('id') != None:
		try: 
			field.lookupvalue_set.get(pk=data.get('id')).update(status=STATUS_TYPES['ACTIVE'])
		except LookupValue.DoesNotExist, err:
			raise MalformedBody(err)
	else:
		field.addLookupValues(data.get('name'))

	return field

@check_admin
def removeLookupValue(user, project_id, featuretype_id, field_id, lookup_id, project=None):
	field = project.featuretype_set.get(pk=featuretype_id).getField(field_id)
	lookup_value = field.lookupvalue_set.get(pk=lookup_id)
	field.removeLookupValues(lookup_value)
	
	return field