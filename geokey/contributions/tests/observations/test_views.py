import json

from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises
from rest_framework.test import APIRequestFactory, force_authenticate

from geokey.projects.tests.model_factories import UserF, ProjectF
from geokey.projects.models import Project
from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory
)
from geokey.users.tests.model_factories import UserGroupF

from ..model_factories import (
    ObservationFactory, CommentFactory, LocationFactory
)

from geokey.contributions.views.observations import (
    SingleAllContributionAPIView, SingleContributionAPIView,
    ContributionSearchAPIView, ProjectObservations
)
from geokey.contributions.models import Observation


class ContributionSearchTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        category = CategoryFactory.create()
        TextFieldFactory.create(**{'key': 'key', 'category': category})

        ObservationFactory.create_batch(5, **{
            'properties': {'key': 'blah'},
            'project': self.project,
            'category': category
        })
        ObservationFactory.create_batch(5, **{
            'properties': {'key': 'blub'},
            'project': self.project,
            'category': category
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

    def test_get_with_blub(self):
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
        self.viewer = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator],
            add_viewer=[self.viewer]
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

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    def test_approve_pending_with_admin_empty_properties(self):
        self.observation.properties = None
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    def test_suspend_pending_with_admin(self):
        self.observation.status = 'active'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "pending"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    def test_approve_pending_with_moderator(self):
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    @raises(PermissionDenied)
    def test_approve_pending_with_contributor(self):
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    def test_approve_pending_with_contributor_who_is_moderator(self):
        self.moderators.users.add(self.creator)
        self.observation.status = 'pending'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    def test_flag_with_admin(self):
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "pending"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    def test_flag_with_moderator(self):
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "pending"}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'pending')

    def test_flag_with_moderator_and_edit(self):
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {
            'properties': {
                'key': 'updated'
            },
            'meta': {
                'status': 'pending',
            }
        }
        request.user = self.moderator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'pending')
        self.assertEqual(ref.properties.get('key'), 'updated')

    def test_flag_with_contributor(self):
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "pending"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    @raises(PermissionDenied)
    def test_flag_with_anonymous(self):
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "pending"}}
        request.user = AnonymousUser()

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    @raises(PermissionDenied)
    def test_update_user(self):
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'properies': {'text': 'blah'}}
        request.user = self.viewer

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)

    def test_update_under_review(self):
        CommentFactory.create(**{
            'commentto': self.observation,
            'review_status': 'open'
        })
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': 'active'}}
        request.user = self.admin

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)

        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'review')

    @raises(PermissionDenied)
    def test_commit_from_draft_admin(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.admin

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    @raises(PermissionDenied)
    def test_commit_from_draft_with_moderator(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.moderator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    def test_commit_from_draft_with_contributor(self):
        self.moderators.users.add(self.creator)

        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    def test_commit_from_draft_with_contributor_who_is_moderator(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {'meta': {'status': "active"}}
        request.user = self.creator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'pending'
        )

    def test_commit_from_draft_with_contributor_with_data(self):
        self.observation.status = 'draft'
        self.observation.save()

        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.patch(url)
        request.DATA = {
            'properties': {
                'key': 'updated'
            },
            'meta': {
                'status': "active",
            }
        }
        request.user = self.creator

        view = SingleContributionAPIView()
        view.update_and_respond(request, self.observation)
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'pending')
        self.assertEqual(ref.properties.get('key'), 'updated')


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


class ProjectPublicApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category,
            'required': True,
            'order': 1
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category,
            'minval': 0,
            'maxval': 1000,
            'order': 2
        })

        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            }
        }

    def _post(self, data, user):
        url = reverse(
            'api:project_observations',
            kwargs={
                'project_id': self.project.id
            }
        )
        request = self.factory.post(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = ProjectObservations.as_view()
        return view(request, project_id=self.project.id).render()

    def test_contribute_with_wrong_category(self):
        self.data['meta']['category'] = 3864

        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_invalid(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": 12,
                "key_2": "jsdbdjhsb"
            },
            "meta": {
                "category": self.category.id,
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_invalid_number(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": 12,
                "key_2": 2000
            },
            "meta": {
                "category": self.category.id,
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_existing_location(self):
        location = LocationFactory()
        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "location": {
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "private": location.private
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 201)

    def test_contribute_with_private_for_project_location(self):
        location = LocationFactory(**{
            'private': True,
            'private_for_project': self.project
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "location": {
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "private": location.private
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
            }
        }
        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 201)

    def test_contribute_with_wrong_project_location(self):
        project = ProjectF()
        location = LocationFactory(**{
            'private': True,
            'private_for_project': project
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "location": {
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "private": location.private
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_private_location(self):
        location = LocationFactory(**{
            'private': True
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "location": {
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "private": location.private
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_valid_draft(self):
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
                "status": "draft"
            }
        }
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)
        self.assertIn('"status":"draft"', response.content)

    def test_contribute_valid_draft_with_empty_required(self):
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": None,
                "key_2": 12
            },
            "meta": {
                "category": self.category.id,
                "status": "draft"
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            }
        }
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)
        self.assertIn('"status":"draft"', response.content)

    def test_contribute_invalid_draft(self):
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 'Blah'
            },
            "meta": {
                "category": self.category.id,
                "status": "draft"
            },
            "location": {
                "name": "UCL",
                "description": "UCL's main quad",
                "private": True
            },
        }
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_to_public_everyone_with_Anonymous(self):
        self.project.everyone_contributes = 'true'
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, AnonymousUser())
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_admin(self):
        self.project.isprivate = False
        self.project.save()
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)
        self.assertIn('"status":"active"', response.content)

    def test_contribute_to_public_with_contributor(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 201)
        self.assertIn('"status":"pending"', response.content)

    def test_contribute_to_public_with_non_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_public_with_anonymous(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, AnonymousUser())
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_private_with_admin(self):
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_contributor(self):
        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_non_member(self):
        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_private_with_anonymous(self):
        response = self._post(self.data, AnonymousUser())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_admin(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_contributor(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_non_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_Anonymous(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, AnonymousUser())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_deleted_with_admin(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_contributor(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_non_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_anonymous(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, AnonymousUser())
        self.assertEqual(response.status_code, 404)


class GetSingleObservationInProject(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.observation = ObservationFactory(
            **{'project': self.project, 'creator': self.contributor})

    def _get(self, user):
        url = reverse(
            'api:project_single_observation',
            kwargs={
                'project_id': self.project.id,
                'observation_id': self.observation.id
            }
        )
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        view = SingleAllContributionAPIView.as_view()
        return view(
            request, project_id=self.project.id,
            observation_id=self.observation.id).render()

    def test_get_with_admin(self):
        response = self._get(self.admin)
        self.assertEqual(response.status_code, 200)

    def test_get_with_contributor(self):
        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 200)

    def test_get_with_non_member(self):
        user = UserF.create()
        response = self._get(user)
        self.assertEqual(response.status_code, 404)


class UpdateObservationInProject(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category,
            'order': 0
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category,
            'order': 1
        })

        location = LocationFactory()

        self.observation = ObservationFactory.create(**{
            'properties': {
                "key_1": "value 1",
                "key_2": 12,
            },
            'category': self.category,
            'project': self.project,
            'location': location,
            'creator': self.admin,
            'status': 'active'
        })

        self.update_data = {
            "properties": {
                "version": 1,
                "key_2": 15
            }
        }

    def _patch(self, data, user):
        url = reverse(
            'api:project_single_observation',
            kwargs={
                'project_id': self.project.id,
                'observation_id': self.observation.id
            }
        )
        request = self.factory.patch(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = SingleAllContributionAPIView.as_view()
        return view(
            request, project_id=self.project.id,
            observation_id=self.observation.id).render()

    def _delete(self, user):
        url = reverse(
            'api:project_single_observation',
            kwargs={
                'project_id': self.project.id,
                'observation_id': self.observation.id
            }
        )
        request = self.factory.delete(url, content_type='application/json')
        force_authenticate(request, user=user)
        view = SingleAllContributionAPIView.as_view()
        return view(
            request, project_id=self.project.id,
            observation_id=self.observation.id).render()

    def test_update_conflict(self):
        response = self._patch(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        data = {"properties": {"attributes": {"version": 1, "key_2": 2}}}
        response = self._patch(
            data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

    def test_update_location_with_admin(self):
        self.update_data['geometry'] = {
            'type': 'Point',
            'coordinates': [
                -0.1444154977798462,
                51.54671869005856
            ]
        }
        self.update_data['properties']['location'] = {
            'name': 'New name'
        }
        response = self._patch(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.properties.get('key_2'), 15)

        self.assertContains(response, 'New name')
        self.assertContains(response, '-0.144415')

    def test_update_with_admin(self):
        response = self._patch(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.properties.get('key_2'), 15)

    @raises(Observation.DoesNotExist)
    def test_delete_with_admin(self):
        response = self._delete(
            self.admin
        )

        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_with_contributor(self):
        response = self._patch(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 403)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.properties.get('key_2'), 12)

    def test_delete_with_contributor(self):
        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 403)

    def test_update_with_non_member(self):
        response = self._patch(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.observation.properties.get('key_2'), 12)

    def test_delete_with_non_member(self):
        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )


class TestProjectPublicApi(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def get(self, user):
        url = reverse('api:project_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        theview = ProjectObservations.as_view()
        return theview(
            request,
            project_id=self.project.id).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, 200)

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, 200)

    def test_get_with_some_dude(self):
        some_dude = UserF.create()
        response = self.get(some_dude)
        self.assertEqual(response.status_code, 404)

    def test_get_with_anonymous(self):
        response = self.get(AnonymousUser())
        self.assertEqual(response.status_code, 404)
