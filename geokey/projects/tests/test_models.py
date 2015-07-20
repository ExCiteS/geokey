import pytz
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.core import mail

from nose.tools import raises

from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory, LookupFieldFactory,
    LookupValueFactory, DateTimeFieldFactory, DateFieldFactory,
    TimeFieldFactory, MultipleLookupFieldFactory, MultipleLookupValueFactory
)
from geokey.contributions.tests.model_factories import ObservationFactory

from geokey.users.tests.model_factories import UserF, UserGroupF
from geokey.categories.models import Category

from .model_factories import ProjectF
from ..models import Project, Admins


class CreateProjectTest(TestCase):
    def test_create_project(self):
        creator = UserF.create()

        project = Project.create(
            'Test', 'Test desc', True, True, creator
        )
        self.assertIn(creator, project.admins.all())


class ProjectTest(TestCase):
    @raises(Project.DoesNotExist)
    def test_delete_project(self):
        project = ProjectF.create()
        project.delete()
        Project.objects.get(pk=project.id)

    def test_str(self):
        project = ProjectF.create(**{
            'name': 'Name',
            'status': 'inactive',
            'isprivate': False
        })
        self.assertEqual(
            str(project),
            'Name status: inactive private: False'
        )

    def test_get_role(self):
        admin = UserF.create()
        moderator = UserF.create()
        contributor = UserF.create()
        other = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            add_moderators=[moderator],
            add_contributors=[contributor]
        )

        self.assertEqual('administrator', project.get_role(admin))
        self.assertEqual('moderator', project.get_role(moderator))
        self.assertEqual('contributor', project.get_role(contributor))
        self.assertEqual('watcher', project.get_role(other))

    def test_re_order_categories(self):
        project = ProjectF.create()

        category_0 = CategoryFactory.create(**{'project': project})
        category_1 = CategoryFactory.create(**{'project': project})
        category_2 = CategoryFactory.create(**{'project': project})
        category_3 = CategoryFactory.create(**{'project': project})
        category_4 = CategoryFactory.create(**{'project': project})

        project.re_order_categories(
            [category_4.id, category_0.id, category_2.id,
             category_1.id,  category_3.id]
        )

        categories = project.categories.all()

        self.assertTrue(categories.ordered)
        self.assertEqual(categories[0], category_4)
        self.assertEqual(categories[1], category_0)
        self.assertEqual(categories[2], category_2)
        self.assertEqual(categories[3], category_1)
        self.assertEqual(categories[4], category_3)

    def test_re_order_categories_with_false_category(self):
        project = ProjectF.create()

        category_0 = CategoryFactory.create(**{'project': project})
        category_1 = CategoryFactory.create(**{'project': project})
        category_2 = CategoryFactory.create(**{'project': project})
        category_3 = CategoryFactory.create(**{'project': project})
        category_4 = CategoryFactory.create(**{'project': project})

        try:
            project.re_order_categories(
                [category_4.id, category_0.id, category_2.id,
                 category_1.id,  5854]
            )
        except Category.DoesNotExist:
            categories = project.categories.all()

            self.assertTrue(categories.ordered)
            self.assertEqual(categories[0].order, 0)
            self.assertEqual(categories[1].order, 1)
            self.assertEqual(categories[2].order, 2)
            self.assertEqual(categories[3].order, 3)
            self.assertEqual(categories[4].order, 4)


class PrivateProjectTest(TestCase):
    def setUp(self):
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'everyone_contributes': 'false'
        })
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertFalse(self.project.can_access(self.viewer_view))
        self.assertFalse(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_contribute(
            self.project.creator))

        self.assertTrue(self.project.can_contribute(self.moderator_view))
        self.assertTrue(self.project.can_contribute(self.moderator))

        self.assertTrue(self.project.can_contribute(self.contributor_view))
        self.assertTrue(self.project.can_contribute(self.contributor))

        self.assertFalse(self.project.can_contribute(self.viewer_view))
        self.assertFalse(self.project.can_contribute(self.viewer))

        self.assertFalse(self.project.can_contribute(self.some_dude))
        self.assertFalse(self.project.can_contribute(AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_moderate(self.project.creator))

        self.assertTrue(self.project.can_moderate(self.moderator_view))
        self.assertTrue(self.project.can_moderate(self.moderator))

        self.assertFalse(self.project.can_moderate(self.contributor_view))
        self.assertFalse(self.project.can_moderate(self.contributor))

        self.assertFalse(self.project.can_moderate(self.viewer_view))
        self.assertFalse(self.project.can_moderate(self.viewer))

        self.assertFalse(self.project.can_moderate(self.some_dude))
        self.assertFalse(self.project.can_moderate(AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class EveryoneContributesTest(TestCase):
    def test(self):
        project = ProjectF.create(**{
            'isprivate': False,
            'everyone_contributes': 'auth'
        })

        self.assertTrue(project.can_contribute(UserF.create()))
        self.assertFalse(project.can_contribute(AnonymousUser()))

        project = ProjectF.create(**{
            'isprivate': False,
            'everyone_contributes': 'true'
        })

        self.assertTrue(project.can_contribute(UserF.create()))
        self.assertTrue(project.can_contribute(AnonymousUser()))


class PublicProjectTest(TestCase):
    def setUp(self):
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'everyone_contributes': 'false'
        })

        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertTrue(self.project.can_access(self.some_dude))
        self.assertTrue(self.project.can_access(AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_contribute(self.project.creator))

        self.assertTrue(self.project.can_contribute(self.moderator_view))
        self.assertTrue(self.project.can_contribute(self.moderator))

        self.assertTrue(self.project.can_contribute(self.contributor_view))
        self.assertTrue(self.project.can_contribute(self.contributor))

        self.assertFalse(self.project.can_contribute(self.viewer_view))
        self.assertFalse(self.project.can_contribute(self.viewer))

        self.assertFalse(self.project.can_contribute(self.some_dude))
        self.assertFalse(self.project.can_contribute(AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_moderate(self.project.creator))

        self.assertTrue(self.project.can_moderate(self.moderator_view))
        self.assertTrue(self.project.can_moderate(self.moderator))

        self.assertFalse(self.project.can_moderate(self.contributor_view))
        self.assertFalse(self.project.can_moderate(self.contributor))

        self.assertFalse(self.project.can_moderate(self.viewer_view))
        self.assertFalse(self.project.can_moderate(self.viewer))

        self.assertFalse(self.project.can_moderate(self.some_dude))
        self.assertFalse(self.project.can_moderate(AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class ProjectContactAdminsTest(TestCase):
    def test_all_contacts(self):
        admin = UserF.create()
        contributor = UserF.create()
        email_user = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            add_contributors=[contributor]
        )

        project.contact_admins(email_user, 'Test email')
        # Should be 2 because project creator is admin too
        self.assertEquals(len(mail.outbox), 2)

    def test_selected_contacts(self):
        admin = UserF.create()
        contributor = UserF.create()
        email_user = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            add_contributors=[contributor]
        )

        admin_rel = Admins.objects.get(project=project, user=admin)
        admin_rel.contact = False
        admin_rel.save()

        project.contact_admins(email_user, 'Test email')
        self.assertEquals(len(mail.outbox), 1)


class ProjectGetDataTest(TestCase):
    def test_get_data_with_none_rule(self):
        user = UserF.create()
        project = ProjectF.create()
        category_1 = CategoryFactory(**{'project': project})
        category_2 = CategoryFactory(**{'project': project})
        category_3 = CategoryFactory(**{'project': project})

        UserGroupF.create(
            add_users=[user],
            **{'project': project, 'filters': None}
        )

        ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1}
        )
        ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_2}
        )
        ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_3}
        )

        self.assertEqual(project.get_all_contributions(user).count(), 15)

    def test_get_data_category_filter(self):
        user = UserF.create()
        project = ProjectF.create()

        category_1 = CategoryFactory(**{'project': project})
        category_2 = CategoryFactory(**{'project': project})

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {category_1.id: {}}
            }
        )

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'status': 'pending'}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_2}
            )
        self.assertEqual(project.get_all_contributions(user).count(), 10)

    def test_get_data_text_filter(self):
        user = UserF.create()
        project = ProjectF.create()

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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {category_1.id: {'text': 'yes'}}
            }
        )

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'yes %s' % x}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'status': 'pending',
                'properties': {'text': 'yes %s' % x}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_1,
                'properties': {'text': 'no %s' % x}}
            )

            ObservationFactory.create(**{
                'project': project,
                'category': category_2,
                'properties': {'bla': 'yes %s' % x}}
            )

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_number_filter(self):
        user = UserF.create()
        project = ProjectF.create()
        category_1 = CategoryFactory(**{'project': project})
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        NumericFieldFactory.create(**{
            'key': 'bla',
            'category': category_2
        })

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {category_1.id: {'number': {'minval': '15'}}}
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_max_number_filter(self):
        user = UserF.create()
        project = ProjectF.create()
        category_1 = CategoryFactory(**{'project': project})
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        NumericFieldFactory.create(**{
            'key': 'bla',
            'category': category_2
        })

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {category_1.id: {'number': {'maxval': '15'}}}
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_max_number_filter(self):
            user = UserF.create()
            project = ProjectF.create()
            category_1 = CategoryFactory(**{'project': project})
            NumericFieldFactory.create(**{
                'key': 'number',
                'category': category_1
            })
            category_2 = CategoryFactory(**{'project': project})
            NumericFieldFactory.create(**{
                'key': 'bla',
                'category': category_2
            })

            UserGroupF.create(
                add_users=[user],
                **{
                    'project': project,
                    'filters': {
                        category_1.id: {'number': {
                            'minval': '10',
                            'maxval': '22'
                        }}
                    }
                }
            )

            for x in range(0, 5):
                ObservationFactory.create(**{
                    'project': project,
                    'category': category_1,
                    'properties': {'number': 5}}
                )

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
                    'category': category_1,
                    'properties': {'number': 25}}
                )

                ObservationFactory.create(**{
                    'project': project,
                    'category': category_2,
                    'properties': {'number': 12}}
                )

            self.assertEqual(project.get_all_contributions(user).count(), 10)

    def test_get_data_lookup_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'lookup': [lookup_1.id, lookup_2.id]}
                }
            }
        )

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
        self.assertEqual(project.get_all_contributions(user).count(), 10)

    def test_get_data_min_max_datetime_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'date': {
                        'minval': '2014-01-01', 'maxval': '2014-06-09 00:00'}
                    }
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_max_date_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'date': {
                        'minval': '2014-01-01', 'maxval': '2014-06-09'}
                    }
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_date_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'date': {
                        'minval': '2014-01-01'}}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_max_date_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'date': {
                        'maxval': '2014-01-01'}}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_max_time_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'time': {
                        'minval': '10:00', 'maxval': '12:00'}}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_max_inverse_time_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'time': {
                        'minval': '22:00', 'maxval': '8:00'}}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_min_time_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'time': {
                        'minval': '12:00'}}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_max_time_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {'time': {
                        'maxval': '12:00'}}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_created_after(self):
        user = UserF.create()
        project = ProjectF.create()
        category_1 = CategoryFactory(**{'project': project})

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {
                        'min_date': '2013-05-01 00:00:00'}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 10)

    def test_get_created_before(self):
        user = UserF.create()
        project = ProjectF.create()
        category_1 = CategoryFactory(**{'project': project})

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {
                        'max_date': '2013-05-01 00:00:00'}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_created_before_and_after(self):
        user = UserF.create()
        project = ProjectF.create()
        category_1 = CategoryFactory(**{'project': project})

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {
                        'min_date': '2013-01-01 00:00:00',
                        'max_date': '2013-10-01 00:00:00'}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 5)

    def test_get_data_multiple_lookup_filter(self):
        user = UserF.create()
        project = ProjectF.create()
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

        UserGroupF.create(
            add_users=[user],
            **{
                'project': project,
                'filters': {
                    category_1.id: {
                        'lookup': [str(lookup_1.id), str(lookup_2.id)]}
                }
            }
        )

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

        self.assertEqual(project.get_all_contributions(user).count(), 10)
