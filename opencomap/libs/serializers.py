from django.core import serializers
from django.contrib.auth.models import User
from opencomap.apps.backend.models.featuretype import FeatureType, Field, TextField, NumericField, DateTimeField, TrueFalseField, LookupField, LookupValue
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.viewgroup import ViewGroup

from django.db.models.fields import FieldDoesNotExist
from django.db.models.query import QuerySet
from django.utils import six

field_registry = {
	'compact': ['id', 'name', 'users'],
	User: ['id', 'username', 'first_name', 'last_name', 'email'],
	FeatureType: ['id', 'name', 'description', 'status', 'field_set'],

	TextField: ['id', 'key','name', 'description', 'status', 'required'],
	NumericField: ['id', 'key', 'name', 'description', 'status', 'required', 'minval', 'maxval'],
	DateTimeField: ['id', 'key', 'name', 'description', 'status', 'required'],
	TrueFalseField: ['id', 'key', 'name', 'description', 'status', 'required'],
	LookupField: ['id', 'key', 'name', 'description', 'status', 'required', 'lookupvalue_set'],
	LookupValue: ['id', 'key', 'name', 'status'],

	ViewGroup: ['id', 'name', 'description', 'can_admin', 'can_edit', 'can_view', 'can_read', 'users'],
}

def serialize_fields(model, fields):
	field_registry[model] = set(fields)

class DataSerializer(serializers.get_serializer('python')):
	def get_dump_object(self, obj):
		self._current['id'] = obj._get_pk_val()
		return self._current

	def handle_fk_field(self, obj, field):
		related_obj = getattr(obj, field.name)
		value = DataSerializer().serialize([related_obj], compact=True)
		self._current[field.name] = value[0]

	def handle_m2m_field(self, obj, field):
		related_objs = getattr(obj, field.name).all()
		values = DataSerializer().serialize(related_objs)
		self._current[field.name] = values

	def handle_fk_ref(self, obj, field_name):
		try:
			related_objs = getattr(obj, field_name).all()
			values = DataSerializer().serialize(related_objs)
			self._current[field_name[:-4] + 's'] = values
		except AttributeError:
			pass

	def serialize(self, queryset, compact=False, **options):
		if hasattr(queryset, 'model'):
			model = queryset.model
		else:
			model = queryset[0].__class__
		
		if compact and not (model == User):
			options['fields'] = field_registry['compact']
		elif options.get('fields') is None and model in field_registry:
			options['fields'] = field_registry[model]


		# options['indent'] = 4

		# return super(DataSerializer, self).serialize(queryset, **options)
		self.options = options
		self.stream = options.pop("stream", six.StringIO())
		self.selected_fields = options.pop("fields", None)
		self.use_natural_keys = options.pop("use_natural_keys", False)
		if self.use_natural_keys:
		    warnings.warn("``use_natural_keys`` is deprecated; use ``use_natural_foreign_keys`` instead.", PendingDeprecationWarning)
		self.use_natural_foreign_keys = options.pop('use_natural_foreign_keys', False) or self.use_natural_keys
		self.use_natural_primary_keys = options.pop('use_natural_primary_keys', False)

		self.start_serialization()
		self.first = True
		for obj in queryset:
			if model == Field:
				obj = obj.getInstance()
				fields_to_read = field_registry[obj.__class__]
			else:
				fields_to_read = self.selected_fields
			
			self.start_object(obj)


			if fields_to_read is not None:
				for field_name in fields_to_read:
					if field_name[-4:] == '_set':
						self.handle_fk_ref(obj, field_name)

			# Use the concrete parent class' _meta instead of the object's _meta
			# This is to avoid local_fields problems for proxy models. Refs #17717.
			concrete_model = obj._meta.concrete_model
			for field in concrete_model._meta.fields:
				if field.serialize:
					if field.rel is None:
			 			if fields_to_read is None or field.attname in fields_to_read:
							self.handle_field(obj, field)
					else:
						if fields_to_read is None or field.attname[:-3] in fields_to_read:
							self.handle_fk_field(obj, field)

			for field in concrete_model._meta.many_to_many:
				if field.serialize:
					if fields_to_read is None or field.attname in fields_to_read:
						self.handle_m2m_field(obj, field)

			self.end_object(obj)
			if self.first:
			    self.first = False
		self.end_serialization()
		return self.getvalue()


class ObjectSerializer(DataSerializer, serializers.get_serializer('json')):
	def getvalue(self):
		value = super(ObjectSerializer, self).getvalue()
		if self.isList: 
			return value
		else:
			return value.strip('[]\n')

	def serialize(self, obj, **options):
		self.isList = isinstance(obj, QuerySet) or isinstance(obj, list)
		
		if self.isList: q_set = obj
		else: q_set = [obj]
		return super(ObjectSerializer, self).serialize(q_set, **options)