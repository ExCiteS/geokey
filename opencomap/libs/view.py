from django.http import HttpResponse
from django.views.generic import View, ListView
from opencomap.libs.serializers import ObjectSerializer, SingleSerializer

class ResourceView(View):
	serializer = None
	fields = None

	def get_fields(self):
		return self.fields

	def serialize(self, value):
		return self.serializer.serialize(value)

class RessourceListView(ResourceView, ListView):
	serializer = ObjectSerializer()

	def render_to_response(self, context):
		return HttpResponse(self.serialize(context['object_list']), content_type='application/json')