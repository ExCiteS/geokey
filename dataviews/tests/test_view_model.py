from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory
from contributions.tests.model_factories import ObservationFactory

from ..models import View, Rule

from .model_factories import ViewFactory, ViewGroupFactory, RuleFactory


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
