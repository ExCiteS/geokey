import json

from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF
from projects.models import Project
from observationtypes.tests.model_factories import ObservationTypeFactory
from dataviews.tests.model_factories import (
    ViewFactory, RuleFactory
)
from dataviews.models import View
from users.tests.model_factories import UserGroupF, ViewUserGroupFactory

from .model_factories import ObservationFactory, CommentFactory

from ..views import (
    SingleMyContributionAPIView, SingleAllContributionAPIView,
    SingleGroupingContributionAPIView, AllContributionsSingleCommentAPIView,
    GroupingContributionsSingleCommentAPIView, SingleContributionAPIView,
    ContributionSearchAPIView
)
from ..models import Observation


class ContributionSearchTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        ObservationFactory.create_batch(5, **{
            'project': self.project,
            'attributes': {'key': 'blah'}
        })
        ObservationFactory.create_batch(5, **{
            'project': self.project,
            'attributes': {'key': 'blub'}
        })

    def get(self, user, query):
        url = reverse('api:contributions_search', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url + '?query=' + query)
        force_authenticate(request, user=user)
        theview = ContributionSearchAPIView.as_view()
        return theview(request, project_id=self.project.id).render()

    def test_get_with_bl(self):
        response = self.get(self.admin, 'bl')
        self.assertEqual(response.status_code, 200)

        features = json.loads(response.content)
        self.assertEqual(len(features.get('features')), 10)

    def test_get_with_blah(self):
        response = self.get(self.admin, 'blah')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'blub')

        features = json.loads(response.content)
        self.assertEqual(len(features.get('features')), 5)

    def test_get_with_blah(self):
        response = self.get(self.admin, 'blub')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'blah')

        features = json.loads(response.content)
        self.assertEqual(len(features.get('features')), 5)


class SingleContributionAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
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
            'creator': self.creator,
            'status': 'active'
        })

    def test_approve_pending_with_admin(self):
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'active')

    def test_approve_pending_with_moderator(self):
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'active')

    @raises(PermissionDenied)
    def test_approve_pending_with_contributor(self):
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    def test_approve_pending_with_contributor_who_is_moderator(self):
        self.moderators.users.add(self.creator)
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'active')

    def test_flag_with_admin(self):
        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "pending"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    def test_flag_with_moderator(self):
        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "pending"}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'pending')

    def test_flag_with_moderator_and_edit(self):
        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': 'pending', 'key': 'updated', 'review_comment': 'check das'}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'pending')
        self.assertEqual(ref.review_comment, 'check das')
        self.assertNotEqual(ref.attributes.get('key'), 'updated')

    def test_flag_with_contributor(self):
        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "pending"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    def test_flag_with_anonymous(self):
        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "pending"}}
        request.user = AnonymousUser()

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    @raises(PermissionDenied)
    def test_commit_from_draft_admin(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    @raises(PermissionDenied)
    def test_commit_from_draft_with_moderator(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    def test_commit_from_draft_with_contributor(self):
        self.moderators.users.add(self.creator)

        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'active')

    def test_commit_from_draft_with_contributor_who_is_moderator(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properties': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        self.assertEqual(Observation.objects.get(pk=self.observation.id).status, 'pending')

    def test_commit_from_draft_with_contributor_with_data(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.patch(url)
        request.DATA = {
            'properties': {
                'status': "active",
                'attributes': {
                    'key': 'updated'
                }
            }
        }
        request.user = self.creator

        view = SingleContributionAPIView()
        data = view.update_and_respond(request, self.observation)
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'pending')
        self.assertEqual(ref.attributes.get('key'), 'updated')

class SingleAllContributionAPIViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'status': 'active'
        })

    def test_get_object_with_creator(self):
        view = SingleAllContributionAPIView()
        view.get_object(
            self.creator, self.observation.project.id, self.observation.id)

    def test_get_object_with_admin(self):
        view = SingleAllContributionAPIView()
        observation = view.get_object(
            self.admin, self.observation.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(Project.DoesNotExist)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = SingleAllContributionAPIView()
        view.get_object(
            some_dude, self.observation.project.id, self.observation.id)

    @raises(Observation.DoesNotExist)
    def test_get_draft_object_with_admin(self):
        self.observation.status = 'draft'
        self.observation.save()

        view = SingleAllContributionAPIView()
        view.get_object(
            self.admin, self.observation.project.id, self.observation.id)

    def test_api_with_admin(self):
        CommentFactory.create_batch(5, **{'commentto': self.observation})
        factory = APIRequestFactory()
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = factory.get(url)
        force_authenticate(request, user=self.admin)
        theview = SingleAllContributionAPIView.as_view()
        response = theview(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id).render()
        self.assertEqual(response.status_code, 200)


class SingleGroupingContributionAPIViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.non_moderator = UserF.create()
        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        observation_type = ObservationTypeFactory.create(**{
            'project': self.project})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'observationtype': observation_type
        })

        self.view = ViewFactory.create(
            add_viewers=[self.non_moderator],
            **{'project': self.project}
        )
        RuleFactory(**{
            'view': self.view,
            'observation_type': observation_type}
        )

    @raises(View.DoesNotExist)
    def test_get_object_with_creator_not_viewmember(self):
        view = SingleGroupingContributionAPIView()
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

        view = SingleGroupingContributionAPIView()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_admin(self):
        view = SingleGroupingContributionAPIView()
        observation = view.get_object(
            self.admin, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    @raises(Observation.DoesNotExist)
    def test_get_pending_observation_with_non_moderator(self):
        self.observation.status = 'pending'
        self.observation.save()

        view = SingleGroupingContributionAPIView()
        observation = view.get_object(
            self.non_moderator, self.observation.project.id,
            self.view.id, self.observation.id
        )


class SingleMyContributionAPIViewTest(TestCase):
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
        view = SingleMyContributionAPIView()
        observation = view.get_object(
            self.creator, self.observation.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(Observation.DoesNotExist)
    def test_get_object_with_admin(self):
        view = SingleMyContributionAPIView()
        view.get_object(
            self.admin, self.observation.project.id, self.observation.id)

    @raises(Project.DoesNotExist)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = SingleMyContributionAPIView()
        view.get_object(
            some_dude, self.observation.project.id, self.observation.id)


class AllContributionsSingleCommentAPIViewTest(TestCase):
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
        view = AllContributionsSingleCommentAPIView()
        observation = view.get_object(
            self.admin, self.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    def test_get_object_with_creator(self):
        view = AllContributionsSingleCommentAPIView()
        view.get_object(self.creator, self.project.id, self.observation.id)

    @raises(Project.DoesNotExist)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = AllContributionsSingleCommentAPIView()
        view.get_object(some_dude, self.project.id, self.observation.id)


class GroupingContributionsSingleCommentAPIViewTest(TestCase):
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
        view = GroupingContributionsSingleCommentAPIView()
        observation = view.get_object(
            self.admin, self.project.id, self.view.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(View.DoesNotExist)
    def test_get_object_with_creator_not_viewmember(self):
        view = GroupingContributionsSingleCommentAPIView()
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
        view = GroupingContributionsSingleCommentAPIView()
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
        view = GroupingContributionsSingleCommentAPIView()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )
