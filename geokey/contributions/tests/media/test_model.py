from django.test import TestCase

from geokey.contributions.models import ImageFile, VideoFile
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.users.tests.model_factories import UserF

from .model_factories import get_image


class ImageFileTest(TestCase):
    def test_get_type_name(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            image=get_image()
        )
        self.assertEqual(image_file.type_name, 'ImageFile')

    def test_delete_file(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            image=get_image()
        )
        image_file.delete()
        self.assertEquals(image_file.status, 'deleted')


class VideoFileTest(TestCase):
    def test_get_type_name(self):
        image_file = VideoFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )
        self.assertEqual(image_file.type_name, 'VideoFile')
