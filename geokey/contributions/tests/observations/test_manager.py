from django.test import TestCase

from geokey.contributions.models import Observation

from geokey.projects.tests.model_factories import ProjectF, UserF
from geokey.categories.tests.model_factories import (
    CategoryFactory, LookupFieldFactory, LookupValueFactory,
    TextFieldFactory, MultipleLookupFieldFactory, MultipleLookupValueFactory
)
from ..model_factories import ObservationFactory


class ObservationTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        ObservationFactory.create_batch(
            5, **{'status': 'active', 'creator': self.creator})
        ObservationFactory.create_batch(
            5, **{'status': 'draft', 'creator': self.creator})
        ObservationFactory.create_batch(
            5, **{'status': 'pending', 'creator': self.creator})
        ObservationFactory.create_batch(
            5, **{'status': 'deleted', 'creator': self.creator})

    def test_for_creator_moderator(self):
        observations = Observation.objects.all().for_moderator(self.creator)
        self.assertEqual(len(observations), 15)
        for observation in observations:
            self.assertNotIn(
                observation.status,
                ['deleted']
            )

    def test_for_moderator(self):
        observations = Observation.objects.all().for_moderator(UserF.create())
        self.assertEqual(len(observations), 10)
        for observation in observations:
            self.assertNotIn(
                observation.status,
                ['draft', 'deleted']
            )

    def test_for_viewer(self):
        observations = Observation.objects.all().for_viewer(UserF.create())
        self.assertEqual(len(observations), 5)
        for observation in observations:
            self.assertNotIn(
                observation.status,
                ['draft', 'pending', 'deleted']
            )


class TestSearch(TestCase):
    def setUp(self):
        o_type = CategoryFactory.create()
        TextFieldFactory.create(**{'key': 'key', 'category': o_type})

        ObservationFactory.create_batch(5, **{
            'properties': {'key': 'blah'},
            'category': o_type
        })
        ObservationFactory.create_batch(5, **{
            'properties': {'key': 'blub'},
            'category': o_type
        })

    def test_bl(self):
        result = Observation.objects.all().search('bl')
        self.assertEqual(len(result), 10)

    def test_blah(self):
        result = Observation.objects.all().search('blah')
        self.assertEqual(len(result), 5)

        for o in result:
            self.assertEqual(o.properties.get('key'), 'blah')

    def test_blub(self):
        result = Observation.objects.all().search('blub')
        self.assertEqual(len(result), 5)

        for o in result:
            self.assertEqual(o.properties.get('key'), 'blub')

    def test_single_lookup(self):
        project = ProjectF.create()
        category = CategoryFactory.create(**{'project': project})
        lookup = LookupFieldFactory.create(
            **{'category': category, 'key': 'lookup'}
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
            'category': category,
            'properties': {'lookup': kermit.id}
        })
        ObservationFactory.create_batch(3, **{
            'project': project,
            'category': category,
            'properties': {'lookup': gonzo.id}
        })

        result = project.observations.all().search('kermit')
        self.assertEqual(len(result), 3)

        for o in result:
            self.assertEqual(o.properties.get('lookup'), kermit.id)

    def test_multiple_lookup(self):
        project = ProjectF.create()
        category = CategoryFactory.create(**{'project': project})
        lookup = MultipleLookupFieldFactory.create(
            **{'category': category, 'key': 'lookup'}
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
            'category': category,
            'properties': {'lookup': [piggy.id, kermit.id]}
        })
        ObservationFactory.create_batch(3, **{
            'project': project,
            'category': category,
            'properties': {'lookup': [gonzo.id]}
        })

        result = project.observations.all().search('kermit')
        self.assertEqual(len(result), 3)

        for o in result:
            self.assertIn(kermit.id, o.properties.get('lookup'))

        result = project.observations.all().search('piggy')
        self.assertEqual(len(result), 3)

        for o in result:
            self.assertIn(kermit.id, o.properties.get('lookup'))
