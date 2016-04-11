"""Tests for managers of contributions (media files)."""

import os
import glob

from PIL import Image
from StringIO import StringIO

from django.core.files.base import ContentFile
from django.test import TestCase
from django.conf import settings

from nose.tools import raises

from geokey.core.exceptions import FileTypeError
from geokey.core.tests.helpers.image_helpers import get_image
from geokey.contributions.models import MediaFile

from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.users.tests.model_factories import UserFactory
from .model_factories import ImageFileFactory


class ModelManagerTest(TestCase):
    def tearDown(self):
        files = glob.glob(os.path.join(
            settings.MEDIA_ROOT,
            'user-uploads/images/*'
        ))
        for f in files:
            os.remove(f)

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
            creator=UserFactory.create(),
            the_file=get_image()
        )

        self.assertIsNotNone(image_file.image)
        self.assertEqual(image_file.type_name, 'ImageFile')

    @raises(FileTypeError)
    def test_create_not_supported(self):
        xyz_file = StringIO()
        xyz = Image.new('RGBA', size=(50, 50), color=(256, 0, 0))
        xyz.save(xyz_file, 'png')
        xyz_file.seek(0)

        the_file = ContentFile(xyz_file.read(), 'test.xyz')
        the_file.content_type = 'chemical/x-xyz'

        MediaFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            the_file=the_file
        )
