import json
from django.test import TestCase

from contributions.models import Observation

from projects.tests.model_factories import ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, LookupFieldFactory, LookupValueFactory,
    TextFieldFactory, MultipleLookupFieldFactory, MultipleLookupValueFactory
)
from ..model_factories import ObservationFactory


class TestSearch(TestCase):
    def setUp(self):
        o_type = ObservationTypeFactory.create()
        TextFieldFactory.create(**{'key': 'key', 'observationtype': o_type})

        ObservationFactory.create_batch(5, **{
            'attributes': {'key': 'blah'},
            'observationtype': o_type
        })
        ObservationFactory.create_batch(5, **{
            'attributes': {'key': 'blub'},
            'observationtype': o_type
        })

    def test_bl(self):
        result = Observation.objects.all().search('bl')
        self.assertEqual(len(result), 10)

    def test_blah(self):
        result = Observation.objects.all().search('blah')
        self.assertEqual(len(result), 5)

        for o in result:
            self.assertEqual(o.attributes.get('key'), 'blah')

    def test_blub(self):
        result = Observation.objects.all().search('blub')
        self.assertEqual(len(result), 5)

        for o in result:
            self.assertEqual(o.attributes.get('key'), 'blub')

    def test_single_lookup(self):
        project = ProjectF.create()
        category = ObservationTypeFactory.create(**{'project': project})
        lookup = LookupFieldFactory.create(
            **{'observationtype': category, 'key': 'lookup'}
        )
        kermit = LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Kermit'
        })
        gonzo = LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Gonzo'
        })
        ObservationFactory.create_batch(3, **{
            'project': project,
            'observationtype': category,
            'attributes': {'lookup': kermit.id}
        })
        ObservationFactory.create_batch(3, **{
            'project': project,
            'observationtype': category,
            'attributes': {'lookup': gonzo.id}
        })

        result = project.observations.all().search('kermit')
        self.assertEqual(len(result), 3)

        for o in result:
            self.assertEqual(o.attributes.get('lookup'), str(kermit.id))

    def test_multiple_lookup(self):
        project = ProjectF.create()
        category = ObservationTypeFactory.create(**{'project': project})
        lookup = MultipleLookupFieldFactory.create(
            **{'observationtype': category, 'key': 'lookup'}
        )
        kermit = MultipleLookupValueFactory.create(**{
            'field': lookup,
            'name': 'Kermit'
        })
        gonzo = MultipleLookupValueFactory.create(**{
            'field': lookup,
            'name': 'Gonzo'
        })
        piggy = MultipleLookupValueFactory.create(**{
            'field': lookup,
            'name': 'Ms Piggy'
        })
        ObservationFactory.create_batch(3, **{
            'project': project,
            'observationtype': category,
            'attributes': {'lookup': [kermit.id, piggy.id]}
        })
        ObservationFactory.create_batch(3, **{
            'project': project,
            'observationtype': category,
            'attributes': {'lookup': [gonzo.id]}
        })

        result = project.observations.all().search('kermit')
        self.assertEqual(len(result), 3)

        for o in result:
            self.assertIn(kermit.id, json.loads(o.attributes.get('lookup')))

        result = project.observations.all().search('piggy')
        self.assertEqual(len(result), 3)

        for o in result:
            self.assertIn(kermit.id, json.loads(o.attributes.get('lookup')))
