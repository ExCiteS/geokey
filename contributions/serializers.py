import json

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from projects.serializers import ProjectSerializer
from observationtypes.serializer import ObservationTypeSerializer

from .models import Location, Observation


class LocationSerializer(serializers.ModelSerializer):
    private_for_project = ProjectSerializer(read_only=True, partial=True)

    class Meta:
        model = Location
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'private', 'private_for_project')


class ObservationSubSerializer(serializers.ModelSerializer):
    observationtype = ObservationTypeSerializer(read_only=True)

    class Meta:
        model = Observation
        depth = 1
        fields = ('id', 'data', 'version', 'status',
                  'observationtype')


class ObservationSerializer(object):
    def serialize(self, obj):
        location_serializer = LocationSerializer(obj.location)
        observation_serializer = ObservationSubSerializer(obj)
        json_object = {
            'type': 'Feature',
            'geometry': json.loads(obj.location.geometry.geojson),
            'properties': {}
        }
        json_object['properties']['location'] = location_serializer.data
        json_object['properties']['observation'] = observation_serializer.data

        return JSONRenderer().render(json_object)
