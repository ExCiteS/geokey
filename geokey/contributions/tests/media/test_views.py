"""Tests for views of contributions (media files)."""

import json
import os
import glob

from os.path import dirname, normpath, abspath, join

from PIL import Image
from io import BytesIO

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.exceptions import PermissionDenied
from django.conf import settings

from nose.tools import raises
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.renderers import JSONRenderer

from geokey.core.exceptions import MalformedRequestData, FileTypeError
from geokey.core.tests.helpers.image_helpers import get_image
from geokey.projects.tests.model_factories import UserFactory, ProjectFactory
from geokey.contributions.models import MediaFile
from geokey.users.models import User

from geokey.contributions.views.media import (
    MediaAbstractAPIView,
    MediaAPIView,
    SingleMediaAPIView
)

from ..model_factories import ObservationFactory
from .model_factories import ImageFileFactory


class MediaFileAbstractListAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        self.contribution = ObservationFactory.create(
            **{'project': self.project}
        )

    def tearDown(self):
        files = glob.glob(os.path.join(
            settings.MEDIA_ROOT,
            'user-uploads/**/*'
        ))
        for f in files:
            os.remove(f)

    def render(self, response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {'blah': 'blubb'}
        return response.render()

    def process_list_of_audio_files(self, files_list):

        for name, file_path, expected_output_file in files_list:
            url = reverse(
                'api:project_media',
                kwargs={
                    'project_id': self.project.id,
                    'contribution_id': self.contribution.id
                }
            )

            audio_file = File(open(
                normpath(join(
                    dirname(abspath(__file__)),
                    file_path
                )),
                'rb'
            ))

            data = {
                'name': name,
                'description': 'Test sound description',
                'file': audio_file
            }

            request = self.factory.post(url, data)
            request.user = self.admin
            view = MediaAbstractAPIView()
            view.request = request

            response = self.render(
                view.create_and_respond(request, self.contribution)
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
            self.assertEqual(
                response_json.get('file_type'),
                'AudioFile',
                msg='Unexpected file type: {} (should be AudioFile) '
                    'for file "{}"'.format(response_json.get('file_type'), name)
            )
            self.assertIn(expected_output_file, response_json.get('url'))

    def process_list_of_image_files(self, files_list):

        for name, file_path, expected_output_file in files_list:
            url = reverse(
                'api:project_media',
                kwargs={
                    'project_id': self.project.id,
                    'contribution_id': self.contribution.id
                }
            )

            data = {
                'name': name,
                'description': 'Test image description',
                'file': get_image(file_name=file_path)
            }

            request = self.factory.post(url, data)
            request.user = self.admin
            view = MediaAbstractAPIView()
            view.request = request

            response = self.render(
                view.create_and_respond(request, self.contribution)
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
            self.assertEqual(
                response_json.get('file_type'),
                'ImageFile'
            )
            self.assertIsNotNone(response_json.get('url'))
            self.assertIn(expected_output_file, response_json.get('url'))

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
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        response = self.render(
            view.get_list_and_respond(request, self.contribution)
        )
        self.assertEqual(len(json.loads(response.content)), 5)

    def test_create_image_and_respond(self):
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
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        response = self.render(
            view.create_and_respond(request, self.contribution)
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
        self.assertEqual(
            response_json.get('file_type'),
            'ImageFile'
        )
        self.assertIsNotNone(response_json.get('url'))

    @raises(MalformedRequestData)
    def test_create_image_and_respond_without_file(self):
        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        data = {
            'name': 'A test image',
            'description': 'Test image description'
        }

        request = self.factory.post(url, data)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        view.create_and_respond(request, self.contribution)

    @raises(MalformedRequestData)
    def test_create_image_and_respond_without_name(self):
        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        data = {
            'description': 'Test image description',
            'file': get_image()
        }

        request = self.factory.post(url, data)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        view.create_and_respond(request, self.contribution)

    def test_create_document_and_respond(self):
        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        document = File(open(
            normpath(join(
                dirname(abspath(__file__)),
                'files/document_1.pdf'
            )),
            'rb'
        ))

        data = {
            'name': 'A test document',
            'description': 'Test document description',
            'file': document
        }

        request = self.factory.post(url, data)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        response = self.render(
            view.create_and_respond(request, self.contribution)
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
        self.assertEqual(
            response_json.get('file_type'),
            'DocumentFile'
        )
        self.assertIn('document_1.pdf', response_json.get('url'))

    @raises(FileTypeError)
    def test_create_document_and_respond_with_unsupported_type(self):
        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        document = File(open(
            normpath(join(
                dirname(abspath(__file__)),
                'files/document_2.doc'
            )),
            'rb'
        ))

        data = {
            'name': 'A test document',
            'description': 'Test document description',
            'file': document
        }

        request = self.factory.post(url, data)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        view.create_and_respond(request, self.contribution)

    # This test does not work on Travis CI, but can be enabled to run locally.
    # Need to set settings.ENABLE_VIDEO = True and fill in YOUTUBE_* settings.
    # def test_create_video_and_respond(self):
    #     url = reverse(
    #         'api:project_media',
    #         kwargs={
    #             'project_id': self.project.id,
    #             'contribution_id': self.contribution.id
    #         }
    #     )
    #
    #     video_file = File(open(normpath(join(dirname(abspath(__file__)), 'files/video.MOV')), 'rb'))
    #
    #     data = {
    #         'name': 'A test video',
    #         'description': 'Test video description',
    #         'file': video_file
    #     }
    #
    #     request = self.factory.post(url, data)
    #     request.user = self.admin
    #     view = MediaAbstractAPIView()
    #     view.request = request
    #
    #     response = self.render(
    #         view.create_and_respond(request, self.contribution)
    #     )
    #
    #     response_json = json.loads(response.content)
    #     self.assertEqual(
    #         response_json.get('name'),
    #         data.get('name')
    #     )
    #     self.assertEqual(
    #         response_json.get('description'),
    #         data.get('description')
    #     )
    #     self.assertEqual(
    #         response_json.get('creator').get('display_name'),
    #         request.user.display_name
    #     )
    #     self.assertEqual(
    #         response_json.get('file_type'),
    #         'VideoFile'
    #     )
    #     self.assertIsNotNone(response_json.get('url'))

    def test_create_audio_files(self):

        test_data = (
            # name, file_url, expected_output_file
            ('MP3 test sound', 'files/audio_1.mp3', 'audio_1.mp3'),
            ('3GP test sound', 'files/audio_2.3gp', 'audio_2.mp3'),
            ('OPUS test sound', 'files/audio_3.opus', 'audio_3.mp3'),
            ('M4A test sound', 'files/audio_4.m4a', 'audio_4.mp3'),
            ('AMR test sound', 'files/audio_5.amr', 'audio_5.mp3'),
            ('AIFF test sound', 'files/audio_6.aiff', 'audio_6.mp3'),
            ('WAV test sound', 'files/audio_7.wav', 'audio_7.mp3'),
            ('Opus with no extension', 'files/audio_8', 'audio_8.mp3'),
            ('AAC test sound', 'files/audio_9.aac', 'audio_9.mp3'),
            ('Flac test sound', 'files/audio_10.flac', 'audio_10.mp3'),
            ('WMA test sound', 'files/audio_12.wma', 'audio_12.mp3'),
        )

        self.process_list_of_audio_files(files_list=test_data)

    def test_create_image_files(self):

        test_data = (
            # name, file_url, expected_output_file
            ('PNG test image', 'files/image_01.png', 'image_01.png'),
            ('JPG test image', 'files/image_02.jpg', 'image_02.jpg'),
            ('GIF test image', 'files/image_03.gif', 'image_03.gif'),
            ('SVG test image', 'files/image_04.svg', 'image_04.svg'),
            ('TIFF test image', 'files/image_05.tiff', 'image_05.tiff'),
        )

        self.process_list_of_image_files(files_list=test_data)

    def test_text_file_not_allowed(self):

        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        document = File(open(
            normpath(join(
                dirname(abspath(__file__)),
                'files/text_1.txt'
            )),
            'rb'
        ))

        data = {
            'name': 'A test text file',
            'description': 'Test file description',
            'file': document
        }

        request = self.factory.post(url, data)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        with self.assertRaises(FileTypeError):
            self.render(
                view.create_and_respond(request, self.contribution)
            )


class MediaAbstractAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        self.contribution = ObservationFactory.create(
            **{'project': self.project, 'creator': self.creator}
        )

        self.image_file = ImageFileFactory.create(
            **{'contribution': self.contribution, 'creator': self.creator}
        )

    def tearDown(self):
        files = glob.glob(os.path.join(
            settings.MEDIA_ROOT,
            'user-uploads/images/*'
        ))
        for f in files:
            os.remove(f)

    def render(self, response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {'blah': 'blubb'}
        return response.render()

    def test_get_single_and_respond(self):
        url = reverse(
            'api:project_single_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id,
                'file_id': self.image_file.id
            }
        )

        request = self.factory.get(url)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        response = self.render(
            view.get_single_and_respond(
                request,
                self.image_file
            )
        )
        response_json = json.loads(response.content)
        self.assertEqual(response_json.get('id'), self.image_file.id)

    @raises(MediaFile.DoesNotExist)
    def test_delete_and_respond_with_admin(self):
        url = reverse(
            'api:project_single_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id,
                'file_id': self.image_file.id
            }
        )

        request = self.factory.delete(url)
        request.user = self.admin
        view = MediaAbstractAPIView()
        view.request = request

        view.delete_and_respond(request, self.contribution, self.image_file)
        MediaFile.objects.get(pk=self.image_file.id)

    @raises(MediaFile.DoesNotExist)
    def test_delete_and_respond_with_contributor(self):
        url = reverse(
            'api:project_single_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id,
                'file_id': self.image_file.id
            }
        )

        request = self.factory.delete(url)
        request.user = self.creator
        view = MediaAbstractAPIView()
        view.request = request

        view.delete_and_respond(request, self.contribution, self.image_file)
        MediaFile.objects.get(pk=self.image_file.id)

    @raises(PermissionDenied)
    def test_delete_and_respond_with_some_dude(self):
        url = reverse(
            'api:project_single_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id,
                'file_id': self.image_file.id
            }
        )

        request = self.factory.delete(url)
        request.user = UserFactory.create()
        view = MediaAbstractAPIView()
        view.request = request

        view.delete_and_respond(request, self.contribution, self.image_file)


class MediaAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.viewer = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        self.contribution = ObservationFactory.create(
            **{'project': self.project, 'creator': self.creator}
        )

        ImageFileFactory.create_batch(5, **{'contribution': self.contribution})

    def tearDown(self):
        files = glob.glob(os.path.join(
            settings.MEDIA_ROOT,
            'user-uploads/images/*'
        ))
        for f in files:
            os.remove(f)

    def get(self, user):
        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        request = self.factory.get(url)
        force_authenticate(request, user)
        view = MediaAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

    def post(self, user, data=None):
        if user.is_anonymous and not User.objects.filter(
                display_name='AnonymousUser').exists():
            UserFactory.create(display_name='AnonymousUser')

        if data is None:
            data = {
                'name': 'A test image',
                'description': 'Test image description',
                'file': get_image()
            }

        url = reverse(
            'api:project_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id
            }
        )

        request = self.factory.post(url, data)
        force_authenticate(request, user)
        view = MediaAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

    def test_get_images_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, 200)

    def test_get_images_with_contributor(self):
        response = self.get(self.creator)
        self.assertEqual(response.status_code, 200)

    def test_get_images_with_some_dude(self):
        response = self.get(UserFactory.create())
        self.assertEqual(response.status_code, 404)

    def test_get_images_with_anonymous(self):
        response = self.get(AnonymousUser())
        self.assertEqual(response.status_code, 404)

    def test_upload_image_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, 201)

    def test_upload_image_with_contributor(self):
        response = self.post(self.creator)
        self.assertEqual(response.status_code, 201)

    def test_upload_image_with_some_dude(self):
        response = self.post(UserFactory.create())
        self.assertEqual(response.status_code, 404)

    def test_upload_image_with_anonymous(self):
        response = self.post(AnonymousUser())
        self.assertEqual(response.status_code, 404)

    def test_post_images_with_anonymous_to_public(self):
        self.project.isprivate = False
        self.project.everyone_contributes = 'true'
        self.project.save()

        response = self.post(AnonymousUser())
        self.assertEqual(response.status_code, 201)

    def test_upload_unsupported_file_format(self):
        xyz_file = BytesIO()
        xyz = Image.new('RGBA', size=(50, 50), color=(256, 0, 0))
        xyz.save(xyz_file, 'png')
        xyz_file.seek(0)

        data = {
            'name': 'A test image',
            'description': 'Test image description',
            'file': ContentFile(xyz_file.read(), 'test.xyz')
        }

        response = self.post(self.admin, data=data)
        self.assertEqual(response.status_code, 400)

    def test_upload_with_loooooong_filename(self):
        data = {
            'name': 'A test image ',
            'description': 'Test image description',
            'file': get_image(file_name='One two three four six seven eight '
                                        'nine ten eleven twelve thirteen '
                                        'fourteen fifteen.png')
        }

        response = self.post(self.admin, data=data)
        self.assertEqual(response.status_code, 201)


class AllContributionsSingleMediaApiViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.viewer = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.creator],
            **{'isprivate': False}
        )

        self.contribution = ObservationFactory.create(
            **{'project': self.project, 'creator': self.creator}
        )

        self.image_file = ImageFileFactory.create(
            **{'contribution': self.contribution, 'creator': self.creator}
        )

    def tearDown(self):
        files = glob.glob(os.path.join(
            settings.MEDIA_ROOT,
            'user-uploads/images/*'
        ))
        for f in files:
            os.remove(f)

    def get(self, user, image_id=None):
        if image_id is None:
            image_id = self.image_file.id

        url = reverse(
            'api:project_single_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id,
                'file_id': image_id
            }
        )

        request = self.factory.get(url)
        force_authenticate(request, user)
        view = SingleMediaAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id,
            file_id=image_id
        ).render()

    def delete(self, user, image_id=None):
        if image_id is None:
            image_id = self.image_file.id

        url = reverse(
            'api:project_single_media',
            kwargs={
                'project_id': self.project.id,
                'contribution_id': self.contribution.id,
                'file_id': image_id
            }
        )

        request = self.factory.delete(url)
        force_authenticate(request, user)
        view = SingleMediaAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id,
            file_id=image_id
        ).render()

    def test_get_image_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_image_with_admin(self):
        response = self.get(self.admin, image_id=545487654)
        self.assertEqual(response.status_code, 404)

    def test_get_image_with_contributor(self):
        response = self.get(self.creator)
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_image_with_contributor(self):
        response = self.get(self.creator, image_id=545487654)
        self.assertEqual(response.status_code, 404)

    def test_get_image_with_some_dude(self):
        response = self.get(UserFactory.create())
        self.assertEqual(response.status_code, 200)

    def test_get_image_with_some_dude_when_project_is_private(self):
        self.project.isprivate = True
        self.project.save()
        response = self.get(UserFactory.create())
        self.assertEqual(response.status_code, 404)

    def test_get_image_with_anonymous(self):
        response = self.get(AnonymousUser())
        self.assertEqual(response.status_code, 200)

    def test_get_image_with_anonymous_when_project_is_private(self):
        self.project.isprivate = True
        self.project.save()
        response = self.get(AnonymousUser())
        self.assertEqual(response.status_code, 404)

    def test_delete_image_with_admin(self):
        response = self.delete(self.admin)
        self.assertEqual(response.status_code, 204)

    def test_delete_non_existing_image_with_admin(self):
        response = self.delete(self.admin, image_id=545487654)
        self.assertEqual(response.status_code, 404)

    def test_delete_image_with_contributor(self):
        response = self.delete(self.creator)
        self.assertEqual(response.status_code, 204)

    def test_delete_non_existing_image_with_contributor(self):
        response = self.delete(self.creator, image_id=545487654)
        self.assertEqual(response.status_code, 404)

    def test_delete_image_with_some_dude(self):
        response = self.delete(UserFactory.create())
        self.assertEqual(response.status_code, 403)

    def test_delete_image_with_anonymous(self):
        response = self.delete(AnonymousUser())
        self.assertEqual(response.status_code, 403)

    def test_delete_anonymous_image_with_image_creator(self):
        image_file = ImageFileFactory.create(**{
            'contribution': self.contribution,
            'creator': User.objects.get(display_name='AnonymousUser')
        })
        response = self.delete(AnonymousUser(), image_id=image_file.id)
        self.assertEqual(response.status_code, 403)
