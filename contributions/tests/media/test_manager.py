from PIL import Image
from StringIO import StringIO

from django.core.files.base import ContentFile
from django.test import TestCase

from nose.tools import raises

from contributions.models import MediaFile

from contributions.tests.model_factories import ObservationFactory
from users.tests.model_factories import UserF
from .model_factories import ImageFileFactory, get_image

class ModelManagerTest(TestCase):
    def test_get_queryset(self):
        ImageFileFactory.create_batch(3)
        files = MediaFile.objects.all()

        self.assertEqual(len(files), 3)
        for f in files:
            self.assertEqual('ImageFile', f.type_name)

    def test_create_image(self):
        image_file = MediaFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            the_file=get_image()
        )
        self.assertEqual(image_file.type_name, 'ImageFile')

    @raises(TypeError)
    def test_create_not_supported(self):
        xyz_file = StringIO()
        xyz = Image.new('RGBA', size=(50,50), color=(256,0,0))
        xyz.save(xyz_file, 'png')
        xyz_file.seek(0)

        image_file = MediaFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            the_file=ContentFile(xyz_file.read(), 'test.xyz')
        )
