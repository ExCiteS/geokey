from opencomap.apps.backend.models.featuretype import FeatureType, LookupValue, FIELD_TYPES
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.libs.exceptions import MalformedBody

from decorators import check_admin
import projects

def get_list(user, project_id):
	project = projects.get_single(user, project_id)
	if project.admins.isMember(user):
		return project.featuretype_set.all()
	else:
		return project.featuretype_set.active()


def get_single(user, project_id, featuretype_id):
	project = projects.get_single(user, project_id)
	featuretype = project.featuretype_set.get(pk=featuretype_id)
	if featuretype.status == STATUS_TYPES['ACTIVE'] or project.admins.isMember(user):
		return featuretype
	else:
		raise PermissionDenied('You are not allowed to access this featuretype.')

@check_admin
def create(user, project_id, data, project=None):
	featuretype = FeatureType(name=data.get('name'), description=data.get('description'), project=project)
	featuretype.save()
	return featuretype

@check_admin
def update(user, project_id, featuretype_id, data, project=None):
	featuretype = project.featuretype_set.get(pk=featuretype_id)
	if data.get('description') != None: featuretype.update(description=data.get('description'))
	if data.get('status') != None: featuretype.update(status=data.get('status'))
	return featuretype

def get_list_field(user, project_id, featuretype_id):
	featuretype = get_single(user, project_id, featuretype_id)
	if featuretype.project.admins.isMember(user):
		return featuretype.field_set.all()
	else:
		return featuretype.field_set.active()

def get_single_field(user, project_id, featuretype_id, field_id):
	featuretype = get_single(user, project_id, featuretype_id)
	field = featuretype.field_set.get(pk=field_id)
	if field.status == STATUS_TYPES['ACTIVE'] or featuretype.project.admins.isMember(user):
		return field
	else:
		raise PermissionDenied('You are not allowed to access this field.')

@check_admin
def createField(user, project_id, featuretype_id, data, project=None):
	featuretype = project.featuretype_set.get(pk=featuretype_id)

	field_model = FIELD_TYPES.get(data.get('type')).get('model')
	required = data.get('required') != None
	field = field_model(name=data.get('name'), description=data.get('description'), required=required, featuretype=featuretype)
	field.save()

	return field


@check_admin
def updateField(user, project_id, featuretype_id, field_id, data, project=None):
	field = project.featuretype_set.get(pk=featuretype_id).getField(field_id)
	if data.get('description') != None: field.update(description=data.get('description'))
	if data.get('status') != None: field.update(status=data.get('status'))
	if data.get('required') != None: field.update(required=data.get('required'))

	try:
		if 'minval' in data: 
			minval = data.get('minval')
		else:
			minval = field.minval
		if 'maxval' in data: 
			maxval = data.get('maxval')
		else:
			maxval = field.maxval

		field.update(minval=minval, maxval=maxval)
	except AttributeError:
		pass
	
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