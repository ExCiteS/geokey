from django.core import serializers

field_registry = {}
def serialize_fields(model, fields):
	field_registry[model] = set(fields)

class DataSerializer(serializers.get_serializer('python')):
	class Meta:
		app_label = 'backend'

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
	class Meta:
		app_label = 'backend'

class SingleSerializer(ObjectSerializer):
	class Meta:
		app_label = 'backend'
	
	def serialize(self, obj, **options):
		return super(SingleSerializer, self).serialize([obj], **options)

	def getvalue(self):
		value = super(SingleSerializer, self).getvalue()
		return value.strip('[]\n')