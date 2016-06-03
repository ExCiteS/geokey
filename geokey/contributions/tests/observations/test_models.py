# -*- coding: utf-8 -*-
"""Tests for models of contributions (observations)."""

import pytz
import datetime

from django.test import TestCase
from django.core.exceptions import ValidationError

from nose.tools import raises

from geokey.contributions.models import Observation
from geokey.projects.tests.model_factories import UserFactory

from geokey.categories.models import LookupValue, MultipleLookupValue
from geokey.categories.tests.model_factories import (
    CategoryFactory, NumericFieldFactory, TextFieldFactory,
    DateTimeFieldFactory, LookupFieldFactory, LookupValueFactory,
    MultipleLookupFieldFactory, MultipleLookupValueFactory
)
from ..model_factories import (
    ObservationFactory, LocationFactory, CommentFactory
)


class TestContributionsPreSave(TestCase):
    def tearDown(self):
        for lookup_value in LookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

        for lookup_value in MultipleLookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

    def test_create_search_index(self):
        category = CategoryFactory.create()
        TextFieldFactory.create(
            **{'key': 'text_1', 'category': category, 'order': 0}
        )
        TextFieldFactory.create(
            **{'key': 'text_2', 'category': category, 'order': 0}
        )
        TextFieldFactory.create(
            **{'key': 'text_3', 'category': category, 'order': 0}
        )
        o = ObservationFactory.create(**{
            'properties': {
                'text_1': 'Blah, abc',
                'text_2': 'blubb blah'
            },
            'category': category
        })
        o.create_search_index()
        o.save()

        reference = Observation.objects.get(pk=o.id)
        self.assertEqual(
            reference.search_index.split(',').sort(),
            'blah,abc,blubb'.split(',').sort()
        )

    def test_create_search_index_lookup(self):
        category = CategoryFactory.create()
        TextFieldFactory.create(
            **{'key': 'text_1', 'category': category, 'order': 0}
        )
        NumericFieldFactory(
            **{'key': 'number', 'category': category, 'order': 0}
        )
        lookup = LookupFieldFactory.create(
            **{'category': category, 'key': 'lookup', 'order': 1}
        )
        kermit = LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Kermit'
        })
        LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Gonzo'
        })

        o = ObservationFactory.create(**{
            'properties': {
                'text_1': 'blah, abc',
                'number': 12,
                'lookup': kermit.id
            },
            'category': category
        })
        o.create_search_index()
        o.save()

        reference = Observation.objects.get(pk=o.id)
        self.assertEqual(
            reference.search_index.split(',').sort(),
            'blah,abc,12,kermit'.split(',').sort()
        )

    def test_create_search_index_multiplelookup(self):
        category = CategoryFactory.create()
        TextFieldFactory.create(
            **{'key': 'text_1', 'category': category, 'order': 0}
        )
        lookup = MultipleLookupFieldFactory.create(
            **{'category': category, 'key': 'lookup', 'order': 2}
        )
        gonzo = MultipleLookupValueFactory.create(**{
            'field': lookup,
            'name': 'Gonzo'
        })
        MultipleLookupValueFactory.create(**{
            'field': lookup,
            'name': 'Ms Piggy'
        })
        kermit = MultipleLookupValueFactory.create(**{
            'field': lookup,
            'name': 'Kermit'
        })

        o = ObservationFactory.create(**{
            'properties': {
                'text_1': 'blah, abc',
                'lookup': [kermit.id, gonzo.id]
            },
            'category': category
        })
        o.create_search_index()
        o.save()

        reference = Observation.objects.get(pk=o.id)
        self.assertEqual(
            reference.search_index.split(',').sort(),
            'blah,abc,gonzo,kermit'.split(',').sort()
        )

    def test_create_search_index_null_multiplelookup(self):
        category = CategoryFactory.create()
        TextFieldFactory.create(
            **{'key': 'text_1', 'category': category, 'order': 0}
        )
        MultipleLookupFieldFactory.create(
            **{'category': category, 'key': 'lookup', 'order': 2}
        )

        o = ObservationFactory.create(**{
            'properties': {
                'text_1': 'blah, abc',
                'lookup': None
            },
            'category': category
        })
        o.create_search_index()
        o.save()

        reference = Observation.objects.get(pk=o.id)
        self.assertEqual(
            reference.search_index.split(',').sort(),
            'blah,abc'.split(',').sort()
        )


class ObservationTest(TestCase):
    @raises(Observation.DoesNotExist)
    def test_delete_observation(self):
        observation = ObservationFactory()
        observation.delete()
        Observation.objects.get(pk=observation.id)

    def test_update_display_field(self):
        category = CategoryFactory()
        field = TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        category.display_field = field
        category.save()

        observation = ObservationFactory(**{
            'project': category.project,
            'category': category,
            'display_field': None,
            'properties': {
                'text': 'blah'
            }
        })

        observation.update_display_field()
        observation.save()

        ref = Observation.objects.get(pk=observation.id)
        self.assertEqual(ref.display_field, 'text:blah')

    def test_update_display_field_empty_properties(self):
        category = CategoryFactory()
        field = TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        category.display_field = field
        category.save()

        observation = ObservationFactory(**{
            'project': category.project,
            'category': category,
            'display_field': None,
            'properties': None
        })

        observation.update_display_field()
        observation.save()

        ref = Observation.objects.get(pk=observation.id)
        self.assertEqual(ref.display_field, 'text:None')

    def test_update_display_field_no_display_field(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        observation = ObservationFactory(**{
            'project': category.project,
            'category': category,
            'display_field': None,
            'properties': None
        })

        observation.update_display_field()
        observation.save()

        ref = Observation.objects.get(pk=observation.id)
        self.assertIsNone(ref.display_field)

    def test_update_expiry_field(self):
        category = CategoryFactory()
        field = DateTimeFieldFactory(**{
            'key': 'expires_at',
            'category': category
        })
        category.expiry_field = field
        category.save()

        observation = ObservationFactory(**{
            'project': category.project,
            'category': category,
            'expiry_field': None,
            'properties': {
                'expires_at': '2016-09-19T15:51:32.804Z'
            }
        })

        observation.update_expiry_field()
        observation.save()

        ref = Observation.objects.get(pk=observation.id)
        self.assertEqual(
            ref.expiry_field,
            datetime.datetime(2016, 9, 19, 15, 51, 32, 804000, tzinfo=pytz.utc)
        )

    def test_update_expiry_field_empty_properties(self):
        category = CategoryFactory()
        field = DateTimeFieldFactory(**{
            'key': 'expires_at',
            'category': category
        })
        category.expiry_field = field
        category.save()

        observation = ObservationFactory(**{
            'project': category.project,
            'category': category,
            'expiry_field': None,
            'properties': None
        })

        observation.update_expiry_field()
        observation.save()

        ref = Observation.objects.get(pk=observation.id)
        self.assertEqual(ref.expiry_field, None)


    def test_update_expiry_field_no_expiry_field(self):
        category = CategoryFactory()
        DateTimeFieldFactory(**{
            'key': 'expires_at',
            'category': category
        })
        observation = ObservationFactory(**{
            'project': category.project,
            'category': category,
            'expiry_field': None,
            'properties': None
        })

        observation.update_expiry_field()
        observation.save()

        ref = Observation.objects.get(pk=observation.id)
        self.assertIsNone(ref.expiry_field)

    def test_update_count(self):
        observation = ObservationFactory()
        CommentFactory.create_batch(5, **{'commentto': observation})
        CommentFactory.create(**{
            'commentto': observation,
            'status': 'deleted'
        })
        observation.update_count()

        ref = Observation.objects.get(pk=observation.id)
        self.assertEqual(ref.num_media, 0)
        self.assertEqual(ref.num_comments, 5)

    def test_create_observation(self):
        creator = UserFactory()
        location = LocationFactory()
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': 'Text', 'number': 12}
        observation = Observation.create(
            properties=data, creator=creator, location=location,
            category=category, project=category.project, status='active'
        )
        self.assertEqual(observation.properties, data)

    def test_create_observation_with_polish_chars(self):
        creator = UserFactory()
        location = LocationFactory()
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'required': True,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': u'śmietnik', 'number': 12}
        observation = Observation.create(
            properties=data, creator=creator, location=location,
            category=category, project=category.project, status='active'
        )
        self.assertEqual(observation.properties, data)

    def test_create_observation_active_default(self):
        creator = UserFactory()
        location = LocationFactory()
        category = CategoryFactory(**{
            'default_status': 'active'
        })
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': 'Text', 'number': 12}
        observation = Observation.create(
            properties=data, creator=creator, location=location,
            category=category, project=category.project, status='active'
        )
        self.assertEqual(observation.properties, data)

    def test_validate_full_inactive_field(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 2
        })
        TextFieldFactory(**{
            'key': 'inactive_text',
            'category': category,
            'status': 'inactive',
            'required': True,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': 'Text', 'number': 12}
        Observation.validate_full(category=category, data=data)

    def test_update_observation(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })

        observation = ObservationFactory.create(**{
            'properties': {'text': 'Text', 'number': 12},
            'category': category,
            'project': category.project
        })

        updater = UserFactory()
        update = {'text': 'Udpated Text', 'number': 13}
        observation.update(properties=update, updator=updater)

        # ref_observation = Observation.objects.get(pk=observation.id)
        self.assertEqual(
            observation.properties,
            {'text': 'Udpated Text', 'number': 13}
        )
        self.assertEqual(observation.version, 2)

    def test_validate_full_with_inactive_field(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        TextFieldFactory(**{
            'key': 'inactive_text',
            'category': category,
            'status': 'inactive',
            'required': True,
            'order': 1
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 2
        })

        observation = ObservationFactory.create(**{
            'properties': {'text': 'Text', 'number': 12},
            'category': category,
            'project': category.project
        })

        updater = UserFactory()
        update = {'text': 'Udpated Text', 'number': 13}
        Observation.validate_full(category=category, data=update)
        observation.update(properties=update, updator=updater)

        self.assertEqual(
            observation.properties,
            {'text': 'Udpated Text', 'number': 13}
        )
        self.assertEqual(observation.version, 2)

    @raises(ValidationError)
    def test_validate_full_invalid(self):
        creator = UserFactory()
        location = LocationFactory()
        category = CategoryFactory()
        TextFieldFactory.create(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': 'Text', 'number': 12}
        observation = Observation.create(
            properties=data, creator=creator, location=location,
            category=category, project=category.project, status='active'
        )

        updater = UserFactory()
        update = {'text': 'Udpated Text', 'number': 'abc', 'version': 1}
        Observation.validate_full(category=category, data=update)
        observation.update(properties=update, updator=updater)

        self.assertEqual(observation.properties, data)
        self.assertEqual(observation.version, 1)

    @raises(ValidationError)
    def test_validate_full_invalid_nubmer(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': 'Text', 'number': 'abc'}
        Observation.validate_full(data=data, category=category)

    @raises(ValidationError)
    def test_validate_full_with_empty_textfield(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'required': True,
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'number': 1000}
        Observation.validate_full(data=data, category=category)

    @raises(ValidationError)
    def test_validate_full_with_zero_textfield(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'required': True,
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'text': '', 'number': 1000}
        Observation.validate_full(data=data, category=category)

    def test_update_draft_observation(self):
        creator = UserFactory()
        location = LocationFactory()
        category = CategoryFactory()
        TextFieldFactory.create(**{
            'key': 'text',
            'category': category,
            'required': True,
            'order': 0
        })
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': category,
            'order': 1
        })
        data = {'number': 12}
        observation = Observation.create(
            properties=data, creator=creator, location=location,
            category=category, project=category.project,
            status='draft'
        )

        updater = UserFactory()
        update = {'number': 13}
        observation.update(properties=update, updator=updater, status='draft')

        self.assertEqual(observation.properties.get('number'), 13)
        self.assertEqual(observation.version, 1)

    @raises(ValidationError)
    def test_validate_full_with_empty_number(self):
        category = CategoryFactory()
        TextFieldFactory(**{
            'key': 'text',
            'category': category,
            'order': 0
        })
        NumericFieldFactory(**{
            'key': 'number',
            'required': True,
            'category': category,
            'order': 1
        })
        data = {'text': 'bla'}
        Observation.validate_full(data=data, category=category)
