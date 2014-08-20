from django.test import TestCase
from django.core.exceptions import ValidationError

from nose.tools import raises

from projects.tests.model_factories import UserF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)

from ..models import Observation, Comment

from .model_factories import (
    LocationFactory, ObservationFactory, CommentFactory
)


class ObservationTest(TestCase):
    @raises(Observation.DoesNotExist)
    def test_delete_observation(self):
        observation = ObservationFactory()
        observation.delete()
        Observation.objects.get(pk=observation.id)

    def test_create_observation(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observationtype
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })
        data = {'text': 'Text', 'number': 12}
        observation = Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )
        self.assertEqual(observation.attributes, data)

    def test_create_observation_with_inactive_field(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observationtype
        })
        TextFieldFactory(**{
            'key': 'inactive_text',
            'observationtype': observationtype,
            'status': 'inactive',
            'required': True
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })
        data = {'text': 'Text', 'number': 12}
        observation = Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )
        self.assertEqual(observation.attributes, data)

    def test_update_observation(self):
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observationtype
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })

        observation = ObservationFactory.create(**{
            'attributes': {'text': 'Text', 'number': 12},
            'observationtype': observationtype,
            'project': observationtype.project
        })

        updater = UserF()
        update = {'text': 'Udpated Text', 'number': 13}
        observation.update(attributes=update, updator=updater)

        # ref_observation = Observation.objects.get(pk=observation.id)
        self.assertEqual(
            observation.attributes,
            {'text': 'Udpated Text', 'number': '13'}
        )
        self.assertEqual(observation.version, 2)

    def test_update_observation_with_inactive_field(self):
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observationtype
        })
        TextFieldFactory(**{
            'key': 'inactive_text',
            'observationtype': observationtype,
            'status': 'inactive',
            'required': True
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })

        observation = ObservationFactory.create(**{
            'attributes': {'text': 'Text', 'number': 12},
            'observationtype': observationtype,
            'project': observationtype.project
        })

        updater = UserF()
        update = {'text': 'Udpated Text', 'number': 13}
        observation.update(attributes=update, updator=updater)

        self.assertEqual(
            observation.attributes,
            {'text': 'Udpated Text', 'number': '13'}
        )
        self.assertEqual(observation.version, 2)

    @raises(ValidationError)
    def test_update_invalid_observation(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory.create(**{
            'key': 'text',
            'observationtype': observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'number',
            'observationtype': observationtype
        })
        data = {'text': 'Text', 'number': 12}
        observation = Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )

        updater = UserF()
        update = {'text': 'Udpated Text', 'number': 'abc', 'version': 1}
        observation.update(attributes=update, updator=updater)

        self.assertEqual(observation.attributes, data)
        self.assertEqual(observation.version, 1)

    @raises(ValidationError)
    def test_create_invalid_observation(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observationtype
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })
        data = {'text': 'Text', 'number': 'abc'}
        Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )

    @raises(ValidationError)
    def test_create_invalid_observation_with_empty_textfield(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'required': True,
            'observationtype': observationtype
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })
        data = {'number': 1000}
        Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )

    @raises(ValidationError)
    def test_create_invalid_observation_with_zero_textfield(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'required': True,
            'observationtype': observationtype
        })
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observationtype
        })
        data = {'text': '', 'number': 1000}
        Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )

    @raises(ValidationError)
    def test_create_invalid_observation_with_empty_number(self):
        creator = UserF()
        location = LocationFactory()
        observationtype = ObservationTypeFactory()
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observationtype
        })
        NumericFieldFactory(**{
            'key': 'number',
            'required': True,
            'observationtype': observationtype
        })
        data = {'text': 'bla'}
        Observation.create(
            attributes=data, creator=creator, location=location,
            observationtype=observationtype, project=observationtype.project
        )

    # ########################################################################
    #
    # COMMENTS
    #
    # ########################################################################


class CommentTest(TestCase):
    @raises(Comment.DoesNotExist)
    def test_delete_comment(self):
        comment = CommentFactory()
        comment.delete()
        Comment.objects.get(pk=comment.id)
