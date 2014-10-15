import json
from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.renderers import JSONRenderer

from projects.tests.model_factories import UserF, ProjectF

from contributions.views import MediaFileListAbstractAPIView

from ..model_factories import ObservationFactory
from .model_factories import ImageFileFactory, get_image

class MediaFileAbstractListAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        self.contribution = ObservationFactory.create(
            **{'project': self.project}
        )

        self.image_file = ImageFileFactory.create(
            **{'contribution': self.contribution}
        )

    def render(self, response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {'blah': 'blubb'}
        return response.render()

    def test_get_list_and_respond(self):
        ImageFileFactory.create_batch(5, **{'contribution': self.contribution})

        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        request = self.factory.get(url)
        view = MediaFileListAbstractAPIView()
        view.request = request

        response = self.render(
            view.get_list_and_respond(self.admin, self.contribution)
        )
        self.assertEqual(len(json.loads(response.content)), 6)

    def test_create_and_respond(self):
        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        data = {
            'name': 'A test image',
            'description': 'Test image description',
            'file': get_image()
        }

        request = self.factory.post(url, data)
        request.user = UserF.create()
        view = MediaFileListAbstractAPIView()
        view.request = request

        response = self.render(
            view.create_and_respond(self.admin, self.contribution)
        )

        response_json = json.loads(response.content)
        self.assertEqual(
            response_json.get('name'),
            data.get('name')
        )
        self.assertEqual(
            response_json.get('description'),
            data.get('description')
        )
        self.assertEqual(
            response_json.get('creator').get('display_name'),
            request.user.display_name
        )
        
