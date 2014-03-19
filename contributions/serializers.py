import json

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from projects.serializers import ProjectSerializer
from users.serializers import UserSerializer
from observationtypes.serializer import ObservationTypeSerializer

from .models import Location, Observation, ObservationData


class LocationSerializer(serializers.ModelSerializer):
    private_for_project = ProjectSerializer(read_only=True, partial=True)

    class Meta:
        model = Location
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'private', 'private_for_project')


class ObservationSerializer(serializers.ModelSerializer):
    observationtype = ObservationTypeSerializer(read_only=True)

    class Meta:
        model = Observation
        depth = 1
        fields = ('id', 'status', 'observationtype')


class ObservationDataSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = ObservationData
        depth = 1
        fields = ('created_at', 'creator', 'version')


class ContributionSerializer(object):
    def serialize(self, obj):
        location_serializer = LocationSerializer(obj.location)
        observation_serializer = ObservationSerializer(obj)
        observation_data_serializer = ObservationDataSerializer(
            obj.current_data)
        json_object = {
            'type': 'Feature',
            'geometry': json.loads(obj.location.geometry.geojson),
            'properties': {}
        }
        json_object['properties']['location'] = location_serializer.data
        json_object['properties'] = dict(
            observation_serializer.data.items() +
            observation_data_serializer.data.items()
        )
        for field in obj.observationtype.fields.all():
            json_object['properties'][field.key] = field.convert_from_string(
                obj.current_data.attributes.get(field.key)
            )

        return JSONRenderer().render(json_object)
