from django.core import serializers
from django.contrib.auth.models import User
from opencomap.apps.backend.models.featuretype import FeatureType, Field, LookupField
from django.db.models.fields import FieldDoesNotExist

field_registry = {
	User: ['id', 'username', 'first_name', 'last_name', 'email'],
	FeatureType: ['id', 'name', 'description', 'status', 'required'],
	Field: ['id', 'name', 'description', 'minval', 'maxval']
}

def serialize_fields(model, fields):
	field_registry[model] = set(fields)

class DataSerializer(serializers.get_serializer('python')):
	def get_dump_object(self, obj):
		self._current['id'] = obj._get_pk_val()
		return self._current

	def handle_fk_field(self, obj, field):
		related_obj = getattr(obj, field.name)
		value = DataSerializer().serialize([related_obj])
		self._current[field.name] = value[0]

	def handle_m2m_field(self, obj, field):
		related_objs = getattr(obj, field.name).all()
		values = DataSerializer().serialize(related_objs)
		self._current[field.name] = values

	def serialize(self, queryset, **options):
		if hasattr(queryset, 'model'):
			model = queryset.model
		else:
			model = queryset[0].__class__

		if options.get('fields') is None and model in field_registry:
			options['fields'] = field_registry[model]

		return super(DataSerializer, self).serialize(queryset, **options)

class ObjectSerializer(DataSerializer, serializers.get_serializer('json')):
	def getvalue(self):
		value = super(ObjectSerializer, self).getvalue()
		if self.single: 
			return value.strip('[]\n')
		else:
			return value

	def serialize(self, obj, **options):
		self.single = (len(obj) == 1)
		return super(ObjectSerializer, self).serialize(obj, **options)

class FeatureTypeSerializer(ObjectSerializer):
	def get_dump_object(self, obj):
		self._current['fields'] = []
		for input_field in obj.field_set.all():

			input_field_dump = {}
			input_field_instance = input_field.getInstance()

			for field_name in field_registry[Field]:
				try:
					field = input_field_instance._meta.get_field(field_name)
					input_field_dump[field_name] = field.value_from_object(input_field_instance)

					try:
						lookup_vals = input_field_instance.lookupvalue_set.all()
						input_field_dump['lookupvalues'] = []

						for value in lookup_vals:
							input_field_dump['lookupvalues'].append({'id': value.id, 'name': value.name})
					except AttributeError:
						continue

				except FieldDoesNotExist:
					continue

			self._current['fields'].append(input_field_dump)

		self._current['id'] = obj._get_pk_val()
		return self._current

	def serialize(self, obj, **options):
		return super(FeatureTypeSerializer, self).serialize(obj, **options)