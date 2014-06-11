import json

from core.exceptions import MalformedRequestData
from django.core.exceptions import ValidationError
from django.test import TestCase
from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)

from ..serializers import ContributionSerializer
from ..models import Observation
from .model_factories import LocationFactory, ObservationFactory


class RestoreLocationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin]
        )
        self.observationtype = ObservationTypeFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })

        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12,
                "observationtype": self.observationtype.id,
                "project": self.project.id,
                "user": self.admin.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

    def test_restore_new_location(self):
        user = UserF.create()
        data = {
            "name": "UCL",
            "description": "UCL's main quad",
            "private": True
        }
        geometry = {
            "type": "Point",
            "coordinates": [
                -0.134046077728271,
                51.52439200896907
            ]
        }
        serializer = ContributionSerializer(data=self.data)
        location = serializer.restore_location(
            data, geometry, user, self.project.id)

        self.assertEqual(location.creator, user)
        self.assertEqual(location.name, 'UCL')
        self.assertEqual(location.description, "UCL's main quad")
        self.assertTrue(location.private)
        self.assertEqual(location.private_for_project, None)
        self.assertEqual(json.loads(location.geometry.geojson), geometry)

    def test_restore_unspecified_location(self):
        user = UserF.create()
        geometry = {
            "type": "Point",
            "coordinates": [
                -0.134046077728271,
                51.52439200896907
            ]
        }
        serializer = ContributionSerializer(data=self.data)
        location = serializer.restore_location(
            None, geometry, user, self.project.id)

        self.assertEqual(location.creator, user)
        self.assertEqual(location.name, None)
        self.assertEqual(location.description, None)
        self.assertFalse(location.private)
        self.assertEqual(location.private_for_project, None)
        self.assertEqual(json.loads(location.geometry.geojson), geometry)


    def test_restore_existing_location(self):
        location = LocationFactory()
        serializer = ContributionSerializer(data=self.data)

        data = {
            "id": location.id,
            "name": location.name,
            "description": location.description,
            "private": location.private
        }
        geometry = json.loads(location.geometry.geojson)

        result = serializer.restore_location(
            data, geometry, self.admin, self.project.id)
        self.assertEqual(location, result)


class ContributionSerializerIntegrationTests(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )
        self.observationtype = ObservationTypeFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })

    def test_create_observation(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12,
                "observationtype": self.observationtype.id,
                "project": self.project.id,
                "user": self.contributor.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

        serializer = ContributionSerializer(data=data)
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(result.get('properties').get('key_1'), 'value 1')
        self.assertEqual(result.get('properties').get('key_2'), 12)
        self.assertEqual(
            result.get('properties').get('observationtype'),
            self.observationtype.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'), 'UCL')
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            "UCL's main quad")

    def test_create_without_speficfied_location(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12,
                "observationtype": self.observationtype.id,
                "project": self.project.id,
                "user": self.contributor.id
            }
        }

        serializer = ContributionSerializer(data=data)
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(result.get('properties').get('key_1'), 'value 1')
        self.assertEqual(result.get('properties').get('key_2'), 12)
        self.assertEqual(
            result.get('properties').get('observationtype'),
            self.observationtype.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'), None)
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            None)

    def test_create_with_existing_location(self):
        location = LocationFactory.create()

        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    location.geometry.coords[0],
                    location.geometry.coords[1]
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12,
                "user": self.contributor.id,
                "observationtype": self.observationtype.id,
                "project": self.project.id,
                "location": {"id": location.id}
            }
        }

        serializer = ContributionSerializer(
            data=data)
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(result.get('properties').get('key_1'), 'value 1')
        self.assertEqual(result.get('properties').get('key_2'), 12)
        self.assertEqual(
            result.get('properties').get('observationtype'),
            self.observationtype.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'),
            location.name)
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            location.description)

    @raises(MalformedRequestData)
    def test_create_with_wrong_location(self):
        project = ProjectF()
        location = LocationFactory(**{
            'private': True,
            'private_for_project': project
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {"id": location.id},
                "observationtype": self.observationtype.id,
                "user": self.contributor.id,
                "project": self.project.id,
                "key_1": "value 1",
                "key_2": 12
            }
        }
        ContributionSerializer(data=data)

    @raises(MalformedRequestData)
    def test_create_with_private_location(self):
        location = LocationFactory(**{'private': True})
        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {"id": location.id},
                "observationtype": self.observationtype.id,
                "project": self.project.id,
                "user": self.contributor.id,
                "key_1": "value 1",
                "key_2": 12
            }
        }
        ContributionSerializer(data=data)

    @raises(ValidationError)
    def test_create_with_invalid_data(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": "blah",
                "observationtype": self.observationtype.id,
                "project": self.project.id,
                "user": self.contributor.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }
        ContributionSerializer(data=data)

    def test_serialize_instance(self):
        observation = ObservationFactory.create()
        TextFieldFactory.create(**{
            'key': 'key',
            'observationtype': observation.observationtype})
        serializer = ContributionSerializer(observation)
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(
            result.get('geometry'),
            json.loads(observation.location.geometry.geojson))
        self.assertEqual(result.get('properties').get('key'), 'value')
        self.assertEqual(
            result.get('properties').get('observationtype'),
            observation.observationtype.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'),
            observation.location.name)
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            observation.location.description)

    def test_serialize_bulk(self):
        ObservationFactory.create_batch(200)
        observations = Observation.objects.select_related()
        serializer = ContributionSerializer(observations, many=True)
        result = serializer.data
        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), 200)

    def test_serialize_update(self):
        observation = ObservationFactory.create(
            **{'attributes': {'number': 12}})
        NumericFieldFactory.create(**{
            'key': 'number',
            'observationtype': observation.observationtype})
        serializer = ContributionSerializer(
            observation,
            data={
                'properties': {
                    'number': 15,
                    'user': observation.project.creator.id
                }
            }
        )
        result = serializer.data

        self.assertEqual(result.get('properties').get('number'), 15)

    @raises(ValidationError)
    def test_serialize_invalid_update(self):
        observation = ObservationFactory.create(
            **{'attributes': {'number': 12}})
        NumericFieldFactory.create(**{
            'key': 'number',
            'observationtype': observation.observationtype})
        ContributionSerializer(
            observation,
            data={
                'properties': {
                    'number': "blah",
                    'user': observation.project.creator.id
                }
            }
        )

        o = Observation.objects.get(pk=observation.id)
        self.assertEqual(o.attributes.get('number'), 12)
