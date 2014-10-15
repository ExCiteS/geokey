from PIL import Image
from StringIO import StringIO

from django.test import TestCase
from django.core.files.base import ContentFile

from nose.tools import raises

from contributions.models import MediaFile, ImageFile

from ..model_factories import ObservationFactory
from users.tests.model_factories import UserF

class MediaFileTest(TestCase):
    @raises(NotImplementedError)
    def test_get_type_name(self):
        media_file = MediaFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create()
        )
        media_file.type_name


class ImageFileTest(TestCase):
    def get_image(self):
        image_file = StringIO()
        image = Image.new('RGBA', size=(50,50), color=(256,0,0))
        image.save(image_file, 'png')
        image_file.seek(0)

        return ContentFile(image_file.read(), 'test.png')

    def test_get_type_name(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            image=self.get_image()
        )
        self.assertEqual(image_file.type_name, 'ImageFile')

