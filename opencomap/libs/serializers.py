from django.core import serializers
from django.contrib.auth.models import User
from opencomap.apps.backend.models.featuretype import FeatureType, Field, LookupField
from django.db.models.fields import FieldDoesNotExist

field_registry = {
	User: ['id', 'username', 'first_name', 'last_name', 'email'],
	FeatureType: ['id', 'name', 'description', 'status', 'required'],
	Field: ['id', 'name', 'description', 'minval', 'maxval', 'status', 'required']
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
	def dump_fields(self, field_set):
		dump = []
		for input_field in field_set:
			dump.append(FieldSerializer().dump_field(input_field.getInstance()))

		return dump


	def get_dump_object(self, obj):
		self._current['fields'] = self.dump_fields(obj.field_set.all())
		self._current['id'] = obj._get_pk_val()
		return self._current

	def serialize(self, obj, **options):
		return super(FeatureTypeSerializer, self).serialize(obj, **options)

class FieldSerializer(ObjectSerializer):
	def dump_field(self, field_instance):
		dump = {}
		for field_name in field_registry[Field]:
			try:
				field = field_instance._meta.get_field(field_name)
				dump[field_name] = field.value_from_object(field_instance)

				try:
					lookup_vals = field_instance.lookupvalue_set.all()
					dump['lookupvalues'] = []

					for value in lookup_vals:
						lookup_dump = {}
						lookup_id = value._meta.get_field('id')
						lookup_dump['id'] = lookup_id.value_from_object(value)

						lookup_name = value._meta.get_field('name')
						lookup_dump['name'] = lookup_name.value_from_object(value)

						lookup_status = value._meta.get_field('status')
						lookup_dump['status'] = lookup_status.value_from_object(value)

						dump['lookupvalues'].append(lookup_dump)
				except AttributeError:
					continue

			except FieldDoesNotExist:
				continue

		return dump


	def get_dump_object(self, obj):
		self._current = self.dump_field(obj.getInstance())
		self._current['id'] = obj._get_pk_val()
		return self._current

	def serialize(self, obj, **options):
		return super(FieldSerializer, self).serialize(obj, **options)