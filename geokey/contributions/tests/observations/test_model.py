# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core.exceptions import ValidationError

from nose.tools import raises

from geokey.contributions.models import Observation, pre_save_update
from geokey.projects.tests.model_factories import UserF

from geokey.categories.tests.model_factories import (
    CategoryFactory, LookupFieldFactory, LookupValueFactory,
    TextFieldFactory, MultipleLookupFieldFactory, MultipleLookupValueFactory,
    NumericFieldFactory
)
from ..model_factories import ObservationFactory, LocationFactory


class TestContributionsPreSave(TestCase):
    def test_pre_save(self):
        o_type = CategoryFactory.create()
        TextFieldFactory.create(
            **{'key': 'key', 'category': o_type, 'order': 0}
        )

        lookup = LookupFieldFactory.create(
            **{'category': o_type, 'key': 'lookup', 'order': 1}
        )
        kermit = LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Kermit'
        })
        LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Gonzo'
        })

        m_lookup = MultipleLookupFieldFactory.create(
            **{'category': o_type, 'key': 'm_lookup', 'order': 2}
        )
        m_kermit = MultipleLookupValueFactory.create(**{
            'field': m_lookup,
            'name': 'Kermit'
        })
        MultipleLookupValueFactory.create(**{
            'field': m_lookup,
            'name': 'Gonzo'
        })
        m_piggy = MultipleLookupValueFactory.create(**{
            'field': m_lookup,
            'name': 'Ms Piggy'
        })

        o = ObservationFactory.create(**{
            'properties': {
                'key': 'blah',
                'lookup': kermit.id,
                'm_lookup': [m_kermit.id, m_piggy.id]
            },
            'category': o_type
        })

        pre_save_update(Observation, instance=o)
        self.assertIn('Ms Piggy', o.search_matches)
        self.assertIn('Kermit', o.search_matches)
        self.assertIn('blah', o.search_matches)


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

    def test_create_observation(self):
        creator = UserF()
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
        creator = UserF()
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
        creator = UserF()
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

        updater = UserF()
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

        updater = UserF()
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
        creator = UserF()
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

        updater = UserF()
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
        creator = UserF()
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

        updater = UserF()
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
