from django.contrib.auth.models import AnonymousUser
from datetime import datetime
import pytz

from django.test import TestCase

from nose.tools import raises

from geokey.projects.tests.model_factories import ProjectF
from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory,
    LookupFieldFactory, LookupValueFactory, DateFieldFactory,
    DateTimeFieldFactory, MultipleLookupFieldFactory,
    MultipleLookupValueFactory, TimeFieldFactory
)
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.users.tests.model_factories import (
    UserF, UserGroupF, GroupingUserGroupFactory
)

from ..models import Grouping, Rule

from .model_factories import (
    GroupingFactory, RuleFactory
)


class TestViewPermissions(TestCase):
    def test_admin(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        view = GroupingFactory.create(**{
            'project': project,
            'isprivate': False
        })

        self.assertTrue(view.can_view(user))
        self.assertTrue(view.can_read(user))
        self.assertTrue(view.can_moderate(user))

    def test_viewer(self):
        user = UserF.create()

        view = GroupingFactory.create()
        group = UserGroupF.create(
            add_users=[user],
            **{'project': view.project, 'can_moderate': False}
        )
        GroupingUserGroupFactory.create(
            **{'grouping': view, 'usergroup': group,
                'can_view': True, 'can_read': False}
        )

        self.assertTrue(view.can_view(user))
        self.assertFalse(view.can_read(user))
        self.assertFalse(view.can_moderate(user))

    def test_reader(self):
        user = UserF.create()

        view = GroupingFactory.create()
        group = UserGroupF.create(
            add_users=[user],
            **{'project': view.project, 'can_moderate': False}
        )
        GroupingUserGroupFactory.create(
            **{'grouping': view, 'usergroup': group,
                'can_view': True, 'can_read': True}
        )

        self.assertTrue(view.can_view(user))
        self.assertTrue(view.can_read(user))
        self.assertFalse(view.can_moderate(user))

    def test_moderator(self):
        user = UserF.create()

        view = GroupingFactory.create()
        group = UserGroupF.create(
            add_users=[user],
            **{'project': view.project, 'can_moderate': True}
        )
        GroupingUserGroupFactory.create(
            **{'grouping': view, 'usergroup': group,
                'can_view': True, 'can_read': True}
        )

        self.assertTrue(view.can_view(user))
        self.assertTrue(view.can_read(user))
        self.assertTrue(view.can_moderate(user))

    def test_some_dude(self):
        user = UserF.create()

        view = GroupingFactory.create()

        self.assertFalse(view.can_view(user))
        self.assertFalse(view.can_read(user))
        self.assertFalse(view.can_moderate(user))

    def test_anonymous(self):
        user = AnonymousUser()
        view = GroupingFactory.create()

        self.assertFalse(view.can_view(user))
        self.assertFalse(view.can_read(user))
        self.assertFalse(view.can_moderate(user))

class RuleTest(TestCase):
    @raises(Rule.DoesNotExist)
    def test_delete_rules(self):
        rule = RuleFactory()
        rule.delete()
        self.assertEqual(rule.status, 'deleted')
        Rule.objects.get(pk=rule.id)

    def test_get_rules(self):
        view = GroupingFactory.create()
        RuleFactory(**{
            'grouping': view,
            'status': 'active'
        })
        RuleFactory(**{
            'grouping': view,
            'status': 'active'
        })
        inactive = RuleFactory(**{
            'grouping': view,
            'status': 'deleted'
        })

        rules = view.rules.all()

        self.assertEqual(len(rules), 2)
        self.assertNotIn(inactive, rules)


class DataGroupingTest(TestCase):
    @raises(Grouping.DoesNotExist)
    def test_delete(self):
        view = GroupingFactory.create()
        view.delete()
        Grouping.objects.get(pk=view.id)

    def test_get_where_clause(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        grouping = GroupingFactory(**{'project': project})

        self.assertIsNone(grouping.get_where_clause())

    def test_get_data(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        category_2 = CategoryFactory(**{'project': project})
        view = GroupingFactory(**{'project': project})
        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1}
            )
            ObservationFactory.create(**{
                'project': project,
                'category': category_2}
            )

        RuleFactory(**{
            'grouping': view,
            'category': category_1
        })

        self.assertEqual(view.data(user).count(), 5)
        for observation in view.data(user):
            self.assertEqual(observation.category, category_1)

    def test_get_updated_data(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'category': category_1
        })

        observation = ObservationFactory.create(**{
            'project': project,
            'category': category_1,
            'properties': {'text': 'yes to update'}
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'yes ' + str(x)}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'no ' + str(x)}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'text': 'yes'}
        })

        updater = UserF()
        update = {'text': 'yes, this has been updated', 'version': 1}
        observation.update(properties=update, updator=updater)
        self.assertEqual(view.data(user).count(), 6)

    def test_get_data_combined(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        category_2 = CategoryFactory(**{'project': project})
        category_3 = CategoryFactory(**{'project': project})
        view = GroupingFactory(**{'project': project})
        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1}
            )
            ObservationFactory.create(**{
                'project': project,
                'category': category_2}
            )
            ObservationFactory.create(**{
                'project': project,
                'category': category_3}
            )

        RuleFactory(**{
            'grouping': view,
            'category': category_1
        })
        RuleFactory(**{
            'grouping': view,
            'category': category_2
        })

        self.assertEqual(view.data(user).count(), 10)
        for observation in view.data(user):
            self.assertNotEqual(
                observation.category, category_3)

    def test_get_data_no_rules(self):
        admin = UserF.create()
        project = ProjectF.create(add_admins=[admin])
        category_1 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'yes ' + str(x)}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'status': 'pending',
                'properties': {'text': 'yes ' + str(x)}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'no ' + str(x)}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': 'yes ' + str(x)}}
            )

        view = GroupingFactory(**{'project': project})
        self.assertEqual(view.data(admin).count(), 0)

    def test_get_data_text_filter(self):
        admin = UserF.create()
        project = ProjectF.create(add_admins=[admin])
        category_1 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'yes ' + str(x)}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'status': 'pending',
                'properties': {'text': 'yes ' + str(x)}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'no ' + str(x)}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': 'yes ' + str(x)}}
            )

        viewer = UserF.create()
        view = GroupingFactory(add_viewers=[viewer], **{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'text': 'yes'}
        })
        self.assertEqual(view.data(admin).count(), 10)
        self.assertEqual(view.data(viewer).count(), 5)

    def test_get_data_min_number_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'number': 12}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'number': 20}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'number': 12}}
            )

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'number': {'minval': '15'}}
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_max_number_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'number': 12}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'number': 20}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'number': 12}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'number': {'maxval': 15}}
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_min_max_number_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'rating',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(5, 11):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'rating': x}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'rating': x}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'rating': x}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'rating': {'minval': 8, 'maxval': 10}}
        })

        self.assertEqual(view.data(user).count(), 6)

    def test_get_data_lookup_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        lookup_field = LookupFieldFactory(**{
            'key': 'lookup',
            'category': category_1
        })
        lookup_1 = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_2 = LookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        category_2 = CategoryFactory(**{'project': project})
        lookup_field_2 = LookupFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })
        lookup_3 = LookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'lookup': lookup_1.id}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'lookup': lookup_2.id}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': lookup_3.id}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'lookup': [lookup_1.id, lookup_2.id]}
        })

        self.assertEqual(view.data(user).count(), 10)

    def test_get_data_min_max_datetime_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        DateTimeFieldFactory(**{
            'key': 'date',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        DateTimeFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2014-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2013-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '2014-04-09'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'date': {
                'minval': '2014-01-01', 'maxval': '2014-06-09 00:00'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_min_max_date_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        DateFieldFactory(**{
            'key': 'date',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        DateFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2014-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2013-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '2014-04-09'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'date': {
                'minval': '2014-01-01', 'maxval': '2014-06-09'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_min_date_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        DateFieldFactory(**{
            'key': 'date',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        DateFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2014-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2013-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '2014-04-09'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'date': {
                'minval': '2014-01-01'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_max_date_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        DateFieldFactory(**{
            'key': 'date',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        DateFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2014-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'date': '2013-04-09'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '2014-04-09'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'date': {
                'maxval': '2014-01-01'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_min_max_time_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'time',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '11:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '18:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '11:00'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'time': {
                'minval': '10:00', 'maxval': '12:00'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_min_max_inverse_time_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'time',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '2:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '18:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '2:00'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'time': {
                'minval': '22:00', 'maxval': '8:00'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_min_time_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'time',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '11:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '18:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '11:00'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'time': {
                'minval': '12:00'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_max_time_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'time',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TimeFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '11:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'time': '18:00'}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': '11:00'}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'time': {
                'maxval': '12:00'}
            }
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_created_after(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2014, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2013, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2012, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'min_date': datetime(2013, 5, 1, 0, 0, 0, tzinfo=pytz.utc)
        })

        self.assertEqual(view.data(user).count(), 10)

    def test_get_created_before(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2014, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2013, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2012, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'max_date': datetime(2013, 5, 1, 0, 0, 0, tzinfo=pytz.utc)
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_created_before_and_after(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2014, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2013, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        obs = ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1
        })

        for o in obs:
            o.created_at = datetime(2012, 7, 23, 10, 34, 1, tzinfo=pytz.utc)
            o.save()

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'min_date': datetime(2013, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
            'max_date': datetime(2013, 10, 1, 0, 0, 0, tzinfo=pytz.utc)
        })

        self.assertEqual(view.data(user).count(), 5)

    def test_get_data_multiple_lookup_filter(self):
        user = UserF.create()
        project = ProjectF.create(add_admins=[user])
        category_1 = CategoryFactory(**{'project': project})
        lookup_field = MultipleLookupFieldFactory(**{
            'key': 'lookup',
            'category': category_1
        })
        lookup_1 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_2 = MultipleLookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        lookup_3 = MultipleLookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field
        })
        category_2 = CategoryFactory(**{'project': project})
        lookup_field_2 = MultipleLookupFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })
        lookup_4 = MultipleLookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field_2
        })

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'lookup': [lookup_1.id, lookup_3.id]}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'lookup': [lookup_2.id, lookup_3.id]}
            })

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': [lookup_4.id]}
            })

        view = GroupingFactory(**{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'lookup': [lookup_1.id, lookup_2.id]}
        })

        self.assertEqual(view.data(user).count(), 10)
