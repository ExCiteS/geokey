import json

from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import PermissionDenied

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from core.exceptions import MalformedRequestData
from projects.models import Project
from projects.serializers import ProjectSerializer
from observationtypes.models import ObservationType
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
    class Meta:
        model = Observation
        depth = 0
        fields = ('id', 'status', 'observationtype')


class ObservationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationData
        depth = 1
        fields = ('created_at', 'version')


class ContributionSerializer(object):
    """
    Serializes and deserializes contribution object from and to its GeoJSON
    conterparts.
    """
    def __init__(self, instance=None, data=None, creator=None):
        """
        Creates a new serializer by deserializing the data dictionary.

        Parameters
        ----------
        instance : contributions.Observation
           An existing observation that is supposed to be updated.
        data : Dictionary
           The data as POSTed with the request. Used to create ob update an
           observation.
        data : creator
           The user signed in with the request
        """

        # Extract the information from the data dictionary
        properties = data.get('properties')
        try:
            location_data = properties.pop('location')
            observationtype_id = properties.pop('observationtype')
            project_id = properties.pop('project')
        except KeyError:
            pass

        if instance is None:
            #Create a new contribution from the GeoJSON data
            project = Project.objects.as_contributor(creator, project_id)
            try:
                observationtype = ObservationType.objects.get_single(
                    creator,
                    project_id,
                    observationtype_id
                )
            except ObservationType.DoesNotExist:
                raise MalformedRequestData('The observationtype can not be '
                                           'used with the project or does not '
                                           'exist.')

            if 'id' in location_data:
                try:
                    location = Location.objects.get_single(
                        creator,
                        project_id,
                        location_data.get('id')
                    )
                except PermissionDenied, error:
                    raise MalformedRequestData(error)
            else:
                location = Location.objects.create(
                    name=location_data.get('name'),
                    description=location_data.get('description'),
                    geometry=GEOSGeometry(
                        json.dumps(data.get('geometry'))
                    ),
                    creator=creator,
                    private=location_data.get('private'),
                    private_for_project=location_data.get(
                        'private_for_project')
                )

            observation = Observation.create(
                data=properties,
                creator=creator,
                location=location,
                project=project,
                observationtype=observationtype
            )
            self.instance = observation
        else:
            # Update the existing contribution
            self.instance = instance
            self.instance.update(data=properties, creator=creator)

    @property
    def data(self):
        """
        Serializes the instance into a GeoJSON format
        """
        location_serializer = LocationSerializer(self.instance.location)
        observation_serializer = ObservationSerializer(self.instance)
        observation_data_serializer = ObservationDataSerializer(
            self.instance.current_data)
        json_object = {
            'type': 'Feature',
            'geometry': json.loads(self.instance.location.geometry.geojson),
            'properties': {}
        }

        json_object['properties'] = dict(
            observation_serializer.data.items() +
            observation_data_serializer.data.items()
        )
        json_object['properties']['location'] = location_serializer.data

        for field in self.instance.observationtype.fields.all():
            json_object['properties'][field.key] = field.convert_from_string(
                self.instance.current_data.attributes.get(field.key)
            )

        return JSONRenderer().render(json_object)
