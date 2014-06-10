import json

from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import PermissionDenied

from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers

from core.exceptions import MalformedRequestData
from projects.models import Project
from observationtypes.models import ObservationType
from observationtypes.serializer import ObservationTypeSerializer
from users.serializers import UserSerializer

from .models import Location, Observation, Comment


class LocationSerializer(geoserializers.GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = ('id', 'name', 'description', 'status', 'created_at')
        write_only_fields = ('status',)


class LocationContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        depth = 1
        fields = ('id', 'name', 'description', 'status', 'created_at')
        write_only_fields = ('status',)


class ObservationSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    updator = UserSerializer()

    class Meta:
        model = Observation
        depth = 0
        fields = (
            'status', 'observationtype', 'review_comment',
            'creator', 'updator', 'created_at', 'version'
        )


class ContributionSerializer(object):
    """
    Serializes and deserializes contribution object from and to its GeoJSON
    conterparts.
    """

    def __init__(self, instance=None, data=None, creator=None, many=False):
        """
        Creates a new serializer by deserializing the data dictionary.

        Parameters
        ----------
        instance : contributions.Observation
           An existing observation that is supposed to be updated.
        data : Dictionary
           The data as POSTed with the request. Used to create ob update an
           observation.
        creator : User
           The user signed in with the request
        """
        self.many = many

        # Extract the information from the data dictionary
        if not self.many and data is not None:
            properties = data.get('properties')

        if instance is None:
            #Create a new contribution from the GeoJSON data
            project_id = properties.pop('project')
            observationtype_id = properties.pop('observationtype')
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

            try:
                location_data = properties.pop('location')
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
                    location = Location(
                        name=location_data.get('name'),
                        description=location_data.get('description'),
                        geometry=GEOSGeometry(
                            json.dumps(data.get('geometry'))
                        ),
                        creator=creator,
                        private=location_data.get('private') or False,
                        private_for_project=location_data.get(
                            'private_for_project')
                    )
            except KeyError:
                location = Location(
                    geometry=GEOSGeometry(json.dumps(data.get('geometry'))),
                    creator=creator
                )

            observation = Observation.create(
                attributes=properties,
                creator=creator,
                location=location,
                project=project,
                observationtype=observationtype
            )
            self.instance = observation
        else:
            self.instance = instance
            # Update the existing contribution
            if not self.many and data is not None:
                self.instance.update(attributes=properties, updator=creator)

    def _serialize_instance(self, instance):
        """
        Serializes the instance into a GeoJSON format
        """
        json_object = {
            'id': instance.id,
            'type': 'Feature',
            'geometry': json.loads(instance.location.geometry.geojson),
            'properties': {}
        }

        observation_serializer = ObservationSerializer(instance)
        json_object['properties'] = observation_serializer.data

        location_serializer = LocationContributionSerializer(
            instance.location)
        json_object['properties']['location'] = location_serializer.data

        observationtype_serializer = ObservationTypeSerializer(
            instance.observationtype)
        json_object['observationtype'] = observationtype_serializer.data

        for field in instance.observationtype.fields.all():
            value = instance.attributes.get(field.key)
            if value is not None:
                json_object['properties'][field.key] = field.convert_from_string(
                    value
                )

        return json_object

    @property
    def data(self):
        if self.many:
            json_object = {
                "type": "FeatureCollection",
                "features": []
            }
            for observation in self.instance:
                json_object['features'].append(
                    self._serialize_instance(observation))

            return json_object
        else:
            return self._serialize_instance(self.instance)


class CommentSerializer(serializers.ModelSerializer):
    creator = UserSerializer()

    def to_native(self, obj):
        native = super(CommentSerializer, self).to_native(obj)
        native['responses'] = CommentSerializer(
            obj.responses.all(), many=True).data

        return native

    class Meta:
        model = Comment
        fields = ('id', 'text', 'creator', 'respondsto', 'created_at')
