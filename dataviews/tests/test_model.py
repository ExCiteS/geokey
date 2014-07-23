from datetime import datetime
import pytz

from django.test import TestCase

from nose.tools import raises

from projects.tests.model_factories import ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    DateTimeFieldFactory
)
from contributions.tests.model_factories import ObservationFactory
from users.tests.model_factories import UserF, UserGroupF, ViewUserGroupFactory

from ..models import View, Rule

from .model_factories import (
    ViewFactory, RuleFactory
)


class TestViewPermissions(TestCase):
    def test_admin(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        view = ViewFactory.create(**{'project': project, 'isprivate': False})

        self.assertTrue(view.can_view(user))
        self.assertTrue(view.can_read(user))
        self.assertTrue(view.can_moderate(user))

    def test_viewer(self):
        user = UserF.create()

        view = ViewFactory.create()
        group = UserGroupF.create(
            add_users=[user],
            **{'project': view.project, 'can_moderate': False}
        )
        ViewUserGroupFactory.create(
            **{'view': view, 'usergroup': group,
                'can_view': True, 'can_read': False}
        )

        self.assertTrue(view.can_view(user))
        self.assertFalse(view.can_read(user))
        self.assertFalse(view.can_moderate(user))

    def test_reader(self):
        user = UserF.create()

        view = ViewFactory.create()
        group = UserGroupF.create(
            add_users=[user],
            **{'project': view.project, 'can_moderate': False}
        )
        ViewUserGroupFactory.create(
            **{'view': view, 'usergroup': group,
                'can_view': True, 'can_read': True}
        )

        self.assertTrue(view.can_view(user))
        self.assertTrue(view.can_read(user))
        self.assertFalse(view.can_moderate(user))

    def test_moderator(self):
        user = UserF.create()

        view = ViewFactory.create()
        group = UserGroupF.create(
            add_users=[user],
            **{'project': view.project, 'can_moderate': True}
        )
        ViewUserGroupFactory.create(
            **{'view': view, 'usergroup': group,
                'can_view': True, 'can_read': True}
        )

        self.assertTrue(view.can_view(user))
        self.assertTrue(view.can_read(user))
        self.assertTrue(view.can_moderate(user))

    def test_some_dude(self):
        user = UserF.create()

        view = ViewFactory.create()

        self.assertFalse(view.can_view(user))
        self.assertFalse(view.can_read(user))
        self.assertFalse(view.can_moderate(user))


class ViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view1_user = UserF.create()
        self.view2_user = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.view1 = ViewFactory(add_viewers=[self.view1_user], **{
            'project': self.project
        })
        self.view2 = ViewFactory(add_viewers=[self.view2_user], **{
            'project': self.project
        })

    @raises(View.DoesNotExist)
    def test_delete(self):
        self.view1.delete()
        View.objects.get(pk=self.view1.id)

    @raises(Rule.DoesNotExist)
    def test_delete_rules(self):
        rule = RuleFactory()
        rule.delete()
        self.assertEqual(rule.status, 'deleted')
        Rule.objects.get(pk=rule.id)

    def test_get_rules(self):
        RuleFactory(**{
            'status': 'active'
        })
        RuleFactory(**{
            'status': 'active'
        })
        inactive = RuleFactory(**{
            'status': 'deleted'
        })
        rules = Rule.objects.all()

        self.assertEqual(len(rules), 2)
        self.assertNotIn(inactive, rules)

    def test_get_data(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )

        RuleFactory(**{'view': view, 'observation_type': observation_type_1})

        self.assertEqual(len(view.data), 5)
        for observation in view.data:
            self.assertEqual(observation.observationtype, observation_type_1)

    def test_get_updated_data(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observation_type_1
        })

        observation = ObservationFactory(**{
            'project': project,
            'observationtype': observation_type_1,
            'attributes': {'text': 'yes to update'}
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'yes ' + str(x)}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'no ' + str(x)}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'text': 'yes'}
        })

        updater = UserF()
        update = {'text': 'yes, this has been updated', 'version': 1}
        observation.update(attributes=update, updator=updater)
        self.assertEqual(len(view.data), 6)

    def test_get_data_combined(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        observation_type_3 = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_3}
            )

        RuleFactory(**{'view': view, 'observation_type': observation_type_1})
        RuleFactory(**{'view': view, 'observation_type': observation_type_2})

        self.assertEqual(len(view.data), 10)
        for observation in view.data:
            self.assertNotEqual(
                observation.observationtype, observation_type_3)

    def test_get_data_text_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'yes ' + str(x)}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'no ' + str(x)}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'bla': 'yes ' + str(x)}}
            )

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'text': 'yes'}
        })
        self.assertEqual(len(view.data), 5)

    def test_get_data_min_number_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 12}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 20}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'number': 12}}
            )

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'number': {'minval': 15}}
        })

        self.assertEqual(len(view.data), 5)

    def test_get_data_max_number_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 12}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 20}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'number': 12}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'number': {'maxval': 15}}
        })

        self.assertEqual(len(view.data), 5)

    def test_get_data_min_max_number_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': x}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': x}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'number': x}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'number': {'minval': 1, 'maxval': 4}}
        })

        self.assertEqual(len(view.data), 4)

    def test_get_data_true_false_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        TrueFalseFieldFactory(**{
            'key': 'true',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        TrueFalseFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'true': True, 'bla': 'bla'}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'true': False}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'true': True}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'true': True}
        })

        self.assertEqual(len(view.data), 5)

    def test_get_data_lookup_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        lookup_field = LookupFieldFactory(**{
            'key': 'lookup',
            'observationtype': observation_type_1
        })
        lookup_1 = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_2 = LookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        lookup_field_2 = LookupFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })
        lookup_3 = LookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'lookup': lookup_1.id}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'lookup': lookup_2.id}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'bla': lookup_3.id}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'lookup': [lookup_1.id, lookup_2.id]}
        })

        self.assertEqual(len(view.data), 10)

    def test_get_data_min_max_date_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        DateTimeFieldFactory(**{
            'key': 'date',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        DateTimeFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'date': '2014-04-09'}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'date': '2013-04-09'}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'bla': '2014-04-09'}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'date': {
                'minval': '2014-01-01', 'maxval': '2014-06-09 00:00'}
            }
        })

        self.assertEqual(len(view.data), 5)

    def test_get_created_after(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2014, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2013, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2012, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'min_date': datetime(2013, 5, 1, 0, 0, 0, tzinfo=pytz.utc)
        })

        self.assertEqual(len(view.data), 10)

    def test_get_created_before(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2014, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2013, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2012, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'max_date': datetime(2013, 5, 1, 0, 0, 0, tzinfo=pytz.utc)
        })

        self.assertEqual(len(view.data), 5)

    def test_get_created_before_and_after(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2014, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2013, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'observationtype': observation_type_1
        })

        for o in obs:
            o.created_at = datetime(2012, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'min_date': datetime(2013, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
            'max_date': datetime(2013, 10, 1, 0, 0, 0, tzinfo=pytz.utc)
        })

        self.assertEqual(len(view.data), 5)
