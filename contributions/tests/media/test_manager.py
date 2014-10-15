from django.test import TestCase

from contributions.models import MediaFile

from .model_factories import ImageFileFactory

class ModelManagerTest(TestCase):
    def test_get_queryset(self):
        ImageFileFactory.create_batch(3)
        files = MediaFile.objects.all()

        self.assertEqual(len(files), 3)
        for f in files:
            self.assertEqual('ImageFile', f.type_name)
