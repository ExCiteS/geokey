from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    DateTimeFieldFactory
)
from contributions.tests.model_factories import (
    ObservationFactory, ObservationDataFactory
)

from ..models import View, Rule

from .model_factories import (
    ViewFactory, ViewGroupFactory, RuleFactory
)


class ViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view1_user = UserF.create()
        self.view2_user = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.view1 = ViewFactory(**{
            'project': self.project
        })
        ViewGroupFactory(add_users=[self.view1_user], **{
            'view': self.view1
        })
        self.view2 = ViewFactory(**{
            'project': self.project
        })
        ViewGroupFactory(add_users=[self.view2_user], **{
            'view': self.view2
        })

    @raises(View.DoesNotExist)
    def test_delete(self):
        self.view1.delete()
        View.objects.get(pk=self.view1.id)

    def test_get_views_with_admin(self):
        views = View.objects.get_list(self.admin, self.project.id)
        self.assertEqual(len(views), 2)

    def test_get_views_with_view1_user(self):
        views = View.objects.get_list(self.view1_user, self.project.id)
        self.assertEqual(len(views), 1)
        self.assertIn(self.view1, views)
        self.assertNotIn(self.view2, views)

    def test_get_views_with_view2_user(self):
        views = View.objects.get_list(self.view2_user, self.project.id)
        self.assertEqual(len(views), 1)
        self.assertIn(self.view2, views)
        self.assertNotIn(self.view1, views)

    def test_get_views_with_contributor(self):
        views = View.objects.get_list(self.contributor, self.project.id)
        self.assertEqual(len(views), 0)

    @raises(PermissionDenied)
    def test_get_views_with_non_member(self):
        View.objects.get_list(self.non_member, self.project.id)

    def test_get_single_view_with_admin(self):
        view = View.objects.get_single(
            self.admin, self.project.id, self.view1.id)
        self.assertEqual(view, self.view1)

    @raises(PermissionDenied)
    def test_get_single_view_with_contributor(self):
        View.objects.get_single(
            self.contributor, self.project.id, self.view1.id)

    def test_get_single_view_with_view_user(self):
        view = View.objects.get_single(
            self.view1_user, self.project.id, self.view1.id)
        self.assertEqual(view, self.view1)

    @raises(PermissionDenied)
    def test_get_single_view_with_wrong_view_user(self):
        View.objects.get_single(
            self.view2_user, self.project.id, self.view1.id)

    @raises(PermissionDenied)
    def test_get_single_view_with_non_member(self):
        View.objects.get_single(
            self.non_member, self.project.id, self.view1.id)

    def test_get_single_view_as_admin_with_admin(self):
        view = View.objects.as_admin(
            self.admin, self.project.id, self.view1.id)
        self.assertEqual(view, self.view1)

    @raises(PermissionDenied)
    def test_get_single_view_as_admin_with_contributor(self):
        View.objects.as_admin(
            self.contributor, self.project.id, self.view1.id)

    @raises(PermissionDenied)
    def test_get_single_view_as_admin_with_view_member(self):
        View.objects.as_admin(
            self.view1_user, self.project.id, self.view1.id)

    @raises(PermissionDenied)
    def test_get_single_view_as_admin_with_non_member(self):
        View.objects.as_admin(
            self.non_member, self.project.id, self.view1.id)

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
            'observationtype': observation_type_1}
        )
        ObservationDataFactory(**{
            'observation': observation,
            'attributes': {'text': 'yes to update'}
        })

        for x in range(0, 5):
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'text': 'yes ' + str(x)}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
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
        observation.update(data=update, creator=updater)

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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'text': 'yes ' + str(x)}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'text': 'no ' + str(x)}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
                'attributes': {'bla': 'yes ' + str(x)}
            })

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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'number': 12}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'number': 20}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
                'attributes': {'number': 12}
            })

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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'number': 12}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'number': 20}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'number': x}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'number': x}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'true': True}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'true': False}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'lookup': lookup_1.id}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'lookup': lookup_2.id}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
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
            observation_1 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_1,
                'attributes': {'date': '2014/04/09'}
            })

            observation_2 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationDataFactory(**{
                'observation': observation_2,
                'attributes': {'date': '2013/04/09'}
            })

            observation_3 = ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationDataFactory(**{
                'observation': observation_3,
                'attributes': {'bla': '2014/04/09'}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'date': {
                'minval': '2014/01/01', 'maxval': '2014/06/09'}
            }
        })

        self.assertEqual(len(view.data), 5)
