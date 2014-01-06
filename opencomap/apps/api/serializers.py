from django.core import serializers

class ObjectSerializer(serializers.get_serializer('json')):
	class Meta:
		app_label = 'api'

	def get_dump_object(self, obj):
		return self._current

class SingleSerializer(ObjectSerializer):
	class Meta:
		app_label = 'api'
	
	def serialize(self, obj, **options):
		return super(SingleSerializer, self).serialize([obj], **options)

	def getvalue(self):
		value = super(SingleSerializer, self).getvalue()
		return value.strip('[]\n')