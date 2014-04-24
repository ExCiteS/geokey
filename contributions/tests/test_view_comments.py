from rest_framework.test import APITestCase

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import UserF, UserGroupF, ProjectF

from .model_factories import ObservationFactory
from ..views import Comments


class AddCommentTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.project = ProjectF.create(**{
            'isprivate': False,
            'admins': UserGroupF(add_users=[self.admin])
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })

    def test_add_comment_to_observation_with_admin(self):
        request = self.factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=self.admin)
        view = Comments.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
