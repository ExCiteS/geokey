"""Tests for serializers of contributions."""

import json

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises

from geokey.projects.tests.model_factories import UserFactory, ProjectFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory
)

from ..serializers import (
    LocationContributionSerializer, ContributionSerializer, CommentSerializer
)

from ..models import Observation, Location
from .model_factories import (
    LocationFactory, ObservationFactory, CommentFactory
)


class LocationContributionSerializerTest(TestCase):
    def test_create_new_full_location(self):
        user = UserFactory.create()
        project = ProjectFactory.create()
        data = {
            "name": "Location",
            "description": "Location description",
            "geometry": '{"type": "Point","coordinates": [ '
                        '-0.144415497779846, 51.54671869005856]}',
            "private": True,
            "private_for_project": project.id
        }
        serializer = LocationContributionSerializer(
            data=data,
            context={'user': user}
        )
        if serializer.is_valid():
            serializer.save()

        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.all()[0].creator, user)

    def test_create_geometry_only(self):
        user = UserFactory.create()
        data = {
            "geometry": '{ "type": "Point","coordinates": [ '
                        '-0.144415497779846, 51.54671869005856] }',
        }
        serializer = LocationContributionSerializer(
            data=data,
            context={'user': user}
        )
        if serializer.is_valid():
            serializer.save()

        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.all()[0].creator, user)

    def test_update_full_location(self):
        user = UserFactory.create()
        location = LocationFactory.create()
        data = {
            "name": "Private Location",
            "private": True,
            "geometry": '{"type": "Point","coordinates": [ '
                        '-0.144415497779846, 51.54671869005856]}',
        }
        serializer = LocationContributionSerializer(
            location,
            data=data,
            context={'user': user}
        )
        if serializer.is_valid():
            serializer.save()

        ref = Location.objects.get(pk=location.id)
        self.assertEqual(ref.name, data.get('name'))
        self.assertEqual(
            json.loads(ref.geometry.geojson),
            json.loads(data.get('geometry'))
        )
        self.assertEqual(ref.private, data.get('private'))

    def test_update_geometry_only(self):
        user = UserFactory.create()
        location = LocationFactory.create()
        data = {
            "geometry": '{"type": "Point","coordinates": [ '
                        '-0.144415497779846, 51.54671869005856]}',
        }
        serializer = LocationContributionSerializer(
            location,
            data=data,
            context={'user': user}
        )
        if serializer.is_valid():
            serializer.save()

        ref = Location.objects.get(pk=location.id)
        self.assertEqual(ref.name, location.name)
        self.assertEqual(
            json.loads(ref.geometry.geojson),
            json.loads(data.get('geometry'))
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
        project = ProjectFactory.create()
        serializer = ContributionSerializer(context={'user': project.creator})
        serializer._errors = {}
        serializer.validate_location(project, 8271839172)
        self.assertIsNotNone(serializer._errors.get('location'))

        project = ProjectFactory.create()
        location = LocationFactory.create(**{'private': True})
        serializer = ContributionSerializer(context={'user': project.creator})
        serializer._errors = {}
        serializer.validate_location(project, location.id)
        self.assertIsNotNone(serializer._errors.get('location'))

        project = ProjectFactory.create()
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


class ContributionSerializerIntegrationTests(TestCase):
    def setUp(self):
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
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
                "private": True,
                "geometry": '{ "type": "Point", "coordinates": ['
                            '-0.134046077728271, 51.52439200896907] }',
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()

        result = serializer.data

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
        self.assertEqual(
            json.loads(data['location']['geometry']),
            json.loads(result['location']['geometry'])
        )

    def test_create_without_speficfied_location(self):
        data = {
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "geometry": '{ "type": "Point", "coordinates": ['
                            '-0.134046077728271, 51.52439200896907] }',
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()
        result = serializer.data

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
        self.assertEqual(
            json.loads(data['location']['geometry']),
            json.loads(result['location']['geometry'])
        )

    def test_create_with_existing_location(self):
        location = LocationFactory.create()

        data = {
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "id": location.id,
                "geometry": location.geometry.geojson
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        serializer.is_valid()
        serializer.save()
        result = serializer.data

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
        self.assertEqual(
            json.loads(data['location']['geometry']),
            json.loads(result['location']['geometry'])
        )

    @raises(ValidationError)
    def test_create_with_wrong_location(self):
        project = ProjectFactory()
        location = LocationFactory(**{
            'private': True,
            'private_for_project': project
        })

        data = {
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "id": location.id,
                "geometry": location.geometry.geojson
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
            "location": {
                "geometry": '{ "type": "Point", "coordinates": ['
                            '-0.134046077728271, 51.52439200896907] }',
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
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id
            },
            "location": {
                "id": location.id,
                "geometry": location.geometry.geojson
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
                "private": True,
                "geometry": '{ "type": "Point", "coordinates": ['
                            '-0.134046077728271, 51.52439200896907] }',
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
        CommentFactory.create(**{
            'commentto': observation
        })
        serializer = ContributionSerializer(
            observation,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(
            result.get('properties').get('key'),
            'value'
        )
        self.assertEqual(
            result.get('meta').get('category').get('id'),
            observation.category.id)
        self.assertEqual(
            result.get('meta').get('num_comments'),
            observation.comments.count())
        self.assertEqual(
            result.get('meta').get('num_media'),
            observation.files_attached.count())
        self.assertEqual(
            result.get('location').get('name'),
            observation.location.name)
        self.assertEqual(
            result.get('location').get('description'),
            observation.location.description)
        self.assertEqual(
            json.loads(observation.location.geometry.geojson),
            json.loads(result['location']['geometry'])
        )

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

        self.assertEqual(len(result), number)

        for f in result:
            self.assertEqual(f.get('meta').get('num_comments'), 0)
            self.assertEqual(f.get('meta').get('num_media'), 0)

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

        self.assertEqual(len(result), number)

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
        user = UserFactory.create()
        comment = CommentFactory.create(**{'creator': user})

        serializer = CommentSerializer(comment, context={'user': user})
        self.assertTrue(serializer.get_isowner(comment))

        serializer = CommentSerializer(
            comment, context={'user': UserFactory.create()})
        self.assertFalse(serializer.get_isowner(comment))

        serializer = CommentSerializer(
            comment, context={'user': AnonymousUser()})
        self.assertFalse(serializer.get_isowner(comment))
