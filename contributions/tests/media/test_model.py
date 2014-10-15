from django.test import TestCase

from nose.tools import raises

from contributions.models import MediaFile, ImageFile

from contributions.tests.model_factories import ObservationFactory
from users.tests.model_factories import UserF

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

