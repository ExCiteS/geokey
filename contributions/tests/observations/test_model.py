from django.test import TestCase

from contributions.models import Observation, update_search_matches

from observationtypes.tests.model_factories import (
    ObservationTypeFactory, LookupFieldFactory, LookupValueFactory,
    TextFieldFactory, MultipleLookupFieldFactory, MultipleLookupValueFactory
)
from ..model_factories import ObservationFactory

class TestContributionsPreSave(TestCase):
    def test_pre_save(self):
        o_type = ObservationTypeFactory.create()
        TextFieldFactory.create(**{'key': 'key', 'observationtype': o_type})

        lookup = LookupFieldFactory.create(
            **{'observationtype': o_type, 'key': 'lookup'}
        )
        kermit = LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Kermit'
        })
        gonzo = LookupValueFactory.create(**{
            'field': lookup,
            'name': 'Gonzo'
        })

        m_lookup = MultipleLookupFieldFactory.create(
            **{'observationtype': o_type, 'key': 'm_lookup'}
        )
        m_kermit = MultipleLookupValueFactory.create(**{
            'field': m_lookup,
            'name': 'Kermit'
        })
        m_gonzo = MultipleLookupValueFactory.create(**{
            'field': m_lookup,
            'name': 'Gonzo'
        })
        m_piggy = MultipleLookupValueFactory.create(**{
            'field': m_lookup,
            'name': 'Ms Piggy'
        })

        o = ObservationFactory.create(**{
            'attributes': {
                'key': 'blah',
                'lookup': kermit.id,
                'm_lookup': [m_kermit.id, m_piggy.id]
            },
            'observationtype': o_type
        })

        update_search_matches(Observation, instance=o)
        self.assertIn('Ms Piggy', o.search_matches)
        self.assertIn('Kermit', o.search_matches)
        self.assertIn('blah', o.search_matches)

        