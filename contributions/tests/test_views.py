from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from nose.tools import raises
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory
from dataviews.tests.model_factories import (
    ViewFactory, RuleFactory
)
from users.tests.model_factories import UserGroupF, ViewUserGroupFactory

from .model_factories import ObservationFactory, CommentFactory

from ..views import (
    MySingleObservation, SingleProjectObservation, SingleViewObservation,
    ProjectComment, ViewComment, SingleObservation
)
from ..models import Observation


class SingleObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.moderator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.moderators = UserGroupF(add_users=[self.moderator], **{
            'project': self.project,
            'can_moderate': True
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_approve_pending_with_admin(self):
        self.observation.status = 'pending'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': "active"}}, self.admin)
        self.assertEqual(data.get('properties').get('status'), 'active')

    def test_approve_pending_with_moderator(self):
        self.observation.status = 'pending'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': "active"}}, self.moderator)
        self.assertEqual(data.get('properties').get('status'), 'active')

    @raises(PermissionDenied)
    def test_approve_pending_with_contributor(self):
        self.observation.status = 'pending'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': "active"}}, self.creator)
        self.assertEqual(data.get('properties').get('status'), 'pending')

    @raises(PermissionDenied)
    def test_approve_pending_with_contributor_who_is_moderator(self):
        self.moderators.users.add(self.creator)
        self.observation.status = 'pending'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': "active"}}, self.creator)
        self.assertEqual(data.get('properties').get('status'), 'pending')

    def test_flag_with_admin(self):
        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': 'pending'}}, self.admin)
        self.assertEqual(data.get('properties').get('status'), 'pending')

    def test_flag_with_moderator(self):
        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': 'pending'}}, self.moderator)
        self.assertEqual(data.get('properties').get('status'), 'pending')

    def test_flag_with_contributor(self):
        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': 'pending'}}, self.creator)
        self.assertEqual(data.get('properties').get('status'), 'pending')

    @raises(PermissionDenied)
    def test_commit_from_draft_admin(self):
        self.observation.status = 'draft'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': 'active'}}, self.admin)
        self.assertEqual(data.get('properties').get('status'), 'draft')

    @raises(PermissionDenied)
    def test_commit_from_draft_with_moderator(self):
        self.observation.status = 'draft'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': 'active'}}, self.moderator)
        self.assertEqual(data.get('properties').get('status'), 'draft')

    def test_commit_from_draft_with_contributor(self):
        self.observation.status = 'draft'
        self.observation.save()

        view = SingleObservation()
        data = view.update_status(
            self.observation, {'properties': {'status': 'active'}}, self.creator)
        self.assertEqual(data.get('properties').get('status'), 'active')


class SingleProjectObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    @raises(PermissionDenied)
    def test_get_object_with_creator(self):
        view = SingleProjectObservation()
        view.get_object(
            self.creator, self.observation.project.id, self.observation.id)

    def test_get_object_with_admin(self):
        view = SingleProjectObservation()
        observation = view.get_object(
            self.admin, self.observation.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = SingleProjectObservation()
        view.get_object(
            some_dude, self.observation.project.id, self.observation.id)

    def test_api_with_admin(self):
        CommentFactory.create_batch(5, **{'commentto': self.observation})
        factory = APIRequestFactory()
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = factory.get(url)
        force_authenticate(request, user=self.admin)
        theview = SingleProjectObservation.as_view()
        response = theview(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id).render()
        self.assertEqual(response.status_code, 200)


class SingleViewObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        observation_type = ObservationTypeFactory(**{'project': self.project})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'observationtype': observation_type
        })

        self.view = ViewFactory(**{'project': self.project})
        RuleFactory(**{
            'view': self.view,
            'observation_type': observation_type}
        )

    @raises(PermissionDenied)
    def test_get_object_with_creator_not_viewmember(self):
        view = SingleViewObservation()
        view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )

    def test_get_object_with_reader(self):
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group, 'can_read': True}
        )

        view = SingleViewObservation()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_admin(self):
        view = SingleViewObservation()
        observation = view.get_object(
            self.admin, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)


class MySingleObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_object_with_creator(self):
        view = MySingleObservation()
        observation = view.get_object(
            self.creator, self.observation.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(Observation.DoesNotExist)
    def test_get_object_with_admin(self):
        view = MySingleObservation()
        view.get_object(
            self.admin, self.observation.project.id, self.observation.id)

    @raises(PermissionDenied)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = MySingleObservation()
        view.get_object(
            some_dude, self.observation.project.id, self.observation.id)


class ProjectCommentTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_object_with_admin(self):
        view = ProjectComment()
        observation = view.get_object(
            self.admin, self.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_creator(self):
        view = ProjectComment()
        view.get_object(self.creator, self.project.id, self.observation.id)

    @raises(PermissionDenied)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = ProjectComment()
        view.get_object(some_dude, self.project.id, self.observation.id)


class ViewCommentTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        observation_type = ObservationTypeFactory(**{'project': self.project})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'observationtype': observation_type
        })

        self.view = ViewFactory(**{'project': self.project})
        RuleFactory(**{
            'view': self.view,
            'observation_type': observation_type}
        )

    def test_get_object_with_admin(self):
        view = ViewComment()
        observation = view.get_object(
            self.admin, self.project.id, self.view.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_creator_not_viewmember(self):
        view = ViewComment()
        view.get_object(
            self.creator, self.project.id, self.view.id, self.observation.id
        )

    def test_get_object_with_creator_is_viewmember(self):
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        view = ViewComment()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_view_member_not_creator(self):
        view_member = UserF.create()
        group = UserGroupF.create(
            add_users=[view_member],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        view = ViewComment()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )
