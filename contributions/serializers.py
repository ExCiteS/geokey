import json

from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import PermissionDenied

from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers

from core.exceptions import MalformedRequestData
from observationtypes.serializer import ObservationTypeSerializer
from observationtypes.models import ObservationType
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
    contributiontype = serializers.SerializerMethodField('get_type')

    class Meta:
        model = Observation
        depth = 0
        fields = (
            'status', 'contributiontype', 'review_comment',
            'creator', 'updator', 'created_at', 'version'
        )

    def get_type(self, observation):
        return observation.observationtype.id


class ContributionSerializer(object):
    """
    Serializes and deserializes contribution object from and to its GeoJSON
    conterparts.
    """
    def __init__(self, instance=None, data=None, many=False, context=None):
        self.many = many
        self.context = context

        if self.many:
            self.instance = instance
        else:
            self.instance = self.restore_object(instance, data)

    @property
    def data(self):
        if self.many:
            features = [self.to_native_min(obj) for obj in self.instance]
            return {
                "type": "FeatureCollection",
                "features": features
            }

        return self.to_native(self.instance)

    def restore_location(self, data, geometry):
        if data is not None:
            if 'id' in data:
                try:
                    return Location.objects.get_single(
                        self.context.get('user'),
                        self.context.get('project').id,
                        data.get('id')
                    )
                except PermissionDenied, error:
                    raise MalformedRequestData(error)
            else:
                return Location(
                    name=data.get('name'),
                    description=data.get('description'),
                    geometry=GEOSGeometry(json.dumps(geometry)),
                    private=data.get('private') or False,
                    private_for_project=data.get('private_for_project'),
                    creator=self.context.get('user')
                )
        else:
            return Location(
                geometry=GEOSGeometry(json.dumps(geometry)),
                creator=self.context.get('user')
            )

    def restore_object(self, instance=None, data=None):
        if data is not None:
            properties = data.get('properties')
            user = self.context.get('user')

            status = 'active'
            if 'status' in properties:
                status = properties.pop('status')

            if instance is not None:
                return instance.update(
                    attributes=properties, updator=user, status=status)
            else:
                project = self.context.get('project')

                try:
                    observationtype = project.observationtypes.get(
                        pk=properties.pop('contributiontype'))
                except ObservationType.DoesNotExist:
                    raise MalformedRequestData('The contributiontype can not'
                                               'be used with the project or '
                                               'does not exist.')

                location = self.restore_location(
                    data.get('properties').pop('location', None),
                    data.get('geometry')
                )

                return Observation.create(
                    attributes=properties,
                    creator=user,
                    location=location,
                    project=observationtype.project,
                    observationtype=observationtype,
                    status=status
                )
        else:
            return instance

    def to_native(self, obj):
        json_object = {
            'id': obj.id,
            'type': 'Feature',
            'geometry': json.loads(obj.location.geometry.geojson),
            'properties': {},
            'isowner': obj.creator == self.context.get('user')
        }

        observation_serializer = ObservationSerializer(obj)
        json_object['properties'] = observation_serializer.data

        location_serializer = LocationContributionSerializer(obj.location)
        json_object['properties']['location'] = location_serializer.data

        observationtype_serializer = ObservationTypeSerializer(
            obj.observationtype)
        json_object['contributiontype'] = observationtype_serializer.data

        comment_serializer = CommentSerializer(obj.comments.all(), many=True)
        json_object['comments'] = comment_serializer.data

        for field in obj.observationtype.fields.all():
            value = obj.attributes.get(field.key)
            if value is not None:
                json_object['properties'][field.key] = field.convert_from_string(value)

        return json_object

    def to_native_min(self, obj):
        location = obj.location

        json_object = {
            'id': obj.id,
            'type': 'Feature',
            'geometry': json.loads(obj.location.geometry.geojson),
            'contributiontype': {
                'id': obj.observationtype.id,
                'name': obj.observationtype.name
            },
            'properties': {
                'status': obj.status,
                'creator': obj.creator.display_name,
                'updator': (obj.updator.display_name
                            if obj.updator is not None else None),
                'created_at': obj.created_at,
                'version': obj.version,
                'location': {
                    'id': location.id,
                    'name': location.name
                }
            },
            'isowner': obj.creator == self.context.get('user')
        }

        return json_object


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
