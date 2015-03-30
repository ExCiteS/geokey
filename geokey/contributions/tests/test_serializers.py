import json

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from nose.tools import raises

from geokey.core.exceptions import MalformedRequestData
from geokey.projects.tests.model_factories import UserF, ProjectF
from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory
)

from ..serializers import ContributionSerializer, CommentSerializer
from ..models import Observation
from .model_factories import (
    LocationFactory, ObservationFactory, CommentFactory
)


class ContributionSerializerTest(TestCase):
    def test_replace_null(self):
        properties = {
            'text': 'blah',
            'number': 2,
            'text_null': ''
        }

        serializer = ContributionSerializer(data={})

        result = serializer.replace_null(properties)
        self.assertIsNone(result.get('text_null'))
        self.assertEqual(result.get('number'), properties.get('number'))
        self.assertEqual(result.get('text'), properties.get('text'))

    def test_validate_location(self):
        project = ProjectF.create()
        serializer = ContributionSerializer(context={'user': project.creator})
        serializer._errors = {}
        serializer.validate_location(project, 8271839172)
        self.assertIsNotNone(serializer._errors.get('location'))

        project = ProjectF.create()
        location = LocationFactory.create(**{'private': True})
        serializer = ContributionSerializer(context={'user': project.creator})
        serializer._errors = {}
        serializer.validate_location(project, location.id)
        self.assertIsNotNone(serializer._errors.get('location'))

        project = ProjectF.create()
        location = LocationFactory.create()
        serializer = ContributionSerializer(context={'user': project.creator})
        serializer._errors = {}
        serializer.validate_location(project, location.id)
        self.assertEqual(serializer._errors, {})

    def test_get_display_field(self):
        observation = ObservationFactory(**{
            'display_field': 'text:blah'
        })

        serializer = ContributionSerializer(observation)
        display_field = serializer.get_display_field(observation)
        self.assertEqual(display_field.get('key'), 'text')
        self.assertEqual(display_field.get('value'), 'blah')


class RestoreLocationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin]
        )
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category,
            'order': 0
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category,
            'order': 1
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
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
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
        serializer = ContributionSerializer(
            data=self.data,
            context={'user': user, 'project': self.project}
        )
        location = serializer.restore_location(data=data, geometry=geometry)

        self.assertEqual(location.creator, user)
        self.assertEqual(location.name, 'UCL')
        self.assertEqual(location.description, "UCL's main quad")
        self.assertTrue(location.private)
        self.assertEqual(location.private_for_project, None)
        self.assertEqual(json.loads(location.geometry.geojson), geometry)

    def test_restore_unspecified_location(self):
        geometry = {
            "type": "Point",
            "coordinates": [
                -0.134046077728271,
                51.52439200896907
            ]
        }
        serializer = ContributionSerializer(
            data=self.data,
            context={'user': self.admin, 'project': self.project}
        )
        location = serializer.restore_location(geometry=geometry)

        self.assertEqual(location.creator, self.admin)
        self.assertEqual(location.name, None)
        self.assertEqual(location.description, None)
        self.assertFalse(location.private)
        self.assertEqual(location.private_for_project, None)
        self.assertEqual(json.loads(location.geometry.geojson), geometry)

    def test_restore_existing_location(self):
        serializer = ContributionSerializer(
            data=self.data,
            context={'user': self.admin, 'project': self.project}
        )
        if serializer.is_valid():
            serializer.save()
        contribution = serializer.instance

        data = {
            "name": 'Location name',
            "description": 'Location description'
        }
        geometry = self.data.get('geometry')

        result = serializer.restore_location(
            contribution.location,
            data=data,
            geometry=geometry
        )
        self.assertEqual(result.name, data.get('name'))

    def test_permssion_denied(self):
        location = LocationFactory.create(
            **{'private': True}
        )

        data = {
            "id": location.id
        }
        geometry = {
            "type": "Point",
            "coordinates": [
                -0.134046077728271,
                51.52439200896907
            ]
        }

        serializer = ContributionSerializer(
            data=self.data,
            context={'user': self.admin, 'project': self.project}
        )

        try:
            serializer.restore_location(data=data, geometry=geometry)
        except MalformedRequestData:
            pass
        else:
            self.fail('PermissionDenied not raised')


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
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category,
            'order': 0
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category,
            'order': 1
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
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()

        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(
            result.get('properties').get('key_1'),
            'value 1'
        )
        self.assertEqual(
            result.get('properties').get('key_2'),
            12
        )
        self.assertEqual(
            result.get('meta').get('category').get('id'),
            self.category.id)
        self.assertEqual(
            result.get('location').get('name'), 'UCL')
        self.assertEqual(
            result.get('location').get('description'),
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
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(
            result.get('properties').get('key_1'),
            'value 1'
        )
        self.assertEqual(
            result.get('properties').get('key_2'),
            12
        )
        self.assertEqual(
            result.get('meta').get('category').get('id'),
            self.category.id)
        self.assertEqual(
            result.get('location').get('name'), None)
        self.assertEqual(
            result.get('location').get('description'),
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
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "id": location.id
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(
            result.get('properties').get('key_1'),
            'value 1'
        )
        self.assertEqual(
            result.get('properties').get('key_2'),
            12
        )
        self.assertEqual(
            result.get('meta').get('category').get('id'),
            self.category.id)
        self.assertEqual(
            result.get('location').get('name'),
            location.name)
        self.assertEqual(
            result.get('location').get('description'),
            location.description)

    @raises(ValidationError)
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
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "id": location.id
            }
        }
        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid(raise_exception=True)

    @raises(ValidationError)
    def test_create_with_inactive_category(self):
        self.category.status = 'inactive'
        self.category.save()

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
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            }
        }
        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid(raise_exception=True)

    @raises(ValidationError)
    def test_create_with_private_location(self):
        location = LocationFactory(**{'private': True})
        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "id": location.id
            }
        }
        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid(raise_exception=True)

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
                "key_2": "blah"
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            }
        }
        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid(raise_exception=True)

    def test_serialize_instance(self):
        observation = ObservationFactory.create(
            **{'properties': {'key': 'value'}}
        )
        TextFieldFactory.create(**{
            'key': 'key',
            'category': observation.category})
        serializer = ContributionSerializer(
            observation,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(
            result.get('geometry'),
            json.loads(observation.location.geometry.geojson))
        self.assertEqual(
            result.get('properties').get('key'),
            'value'
        )
        self.assertEqual(
            result.get('meta').get('category').get('id'),
            observation.category.id)
        self.assertEqual(
            result.get('location').get('name'),
            observation.location.name)
        self.assertEqual(
            result.get('location').get('description'),
            observation.location.description)

    def test_serialize_bulk(self):
        number = 20

        ObservationFactory.create_batch(number)
        observations = Observation.objects.prefetch_related(
            'location', 'category', 'creator', 'updator')

        serializer = ContributionSerializer(
            observations,
            many=True,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), number)

        for f in result.get('features'):
            self.assertIsNone(f.get('search_matches'))

    def test_serialize_bulk_search(self):
        number = 20

        o_type = CategoryFactory.create()
        TextFieldFactory.create(**{
            'category': o_type,
            'key': 'field-1',
            'order': 0
        })
        TextFieldFactory.create(**{
            'category': o_type,
            'key': 'field-2',
            'order': 1
        })
        TextFieldFactory.create(**{
            'category': o_type,
            'key': 'field-3',
            'order': 2
        })

        ObservationFactory.create_batch(
            number,
            **{
                'properties': {
                    'field-1': 'blah',
                    'field-2': 'blabla',
                    'field-3': 'sddsdsfdsf'
                },
                'category': o_type
            }
        )
        observations = Observation.objects.prefetch_related(
            'location', 'category', 'creator', 'updator')

        serializer = ContributionSerializer(
            observations,
            many=True,
            context={
                'user': self.contributor,
                'project': self.project,
                'search': 'bla'
            }
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), number)

        for f in result.get('features'):
            self.assertIsNotNone(f.get('search_matches'))
            self.assertIsNone(
                f.get('search_matches').get('field-3')
            )

    def test_serialize_update(self):
        observation = ObservationFactory.create(
            **{'properties': {'number': 12}})
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': observation.category})
        serializer = ContributionSerializer(
            observation,
            data={
                'properties': {
                    'number': 15
                }
            },
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()
        result = serializer.data

        self.assertEqual(
            result.get('properties').get('number'),
            15
        )

    @raises(ValidationError)
    def test_serialize_invalid_update(self):
        observation = ObservationFactory.create(
            **{'properties': {'number': 12}})
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': observation.category})
        serializer = ContributionSerializer(
            observation,
            data={
                'properties': {
                    'number': "blah"
                }
            },
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid(raise_exception=True)

        o = Observation.objects.get(pk=observation.id)
        self.assertEqual(o.attributes.get('number'), 12)


class CommendSerializerTest(TestCase):
    def test_get_isowner(self):
        user = UserF.create()
        comment = CommentFactory.create(**{'creator': user})

        serializer = CommentSerializer(comment, context={'user': user})
        self.assertTrue(serializer.get_isowner(comment))

        serializer = CommentSerializer(
            comment, context={'user': UserF.create()})
        self.assertFalse(serializer.get_isowner(comment))

        serializer = CommentSerializer(
            comment, context={'user': AnonymousUser()})
        self.assertFalse(serializer.get_isowner(comment))
