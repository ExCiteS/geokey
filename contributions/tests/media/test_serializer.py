import os
import glob

from django.test import TestCase
from django.conf import settings

from users.tests.model_factories import UserF

from .model_factories import ImageFileFactory, VideoFileFactory
from contributions.serializers import FileSerializer


class FileSerializerTest(TestCase):
    def tearDown(self):
        files = glob.glob(os.path.join(
            settings.MEDIA_ROOT,
            'user-uploads/images/*'
        ))
        for f in files:
            os.remove(f)

    def test_get_is_owner(self):
        image = ImageFileFactory.create()

        serializer = FileSerializer(image, context={'user': image.creator})
        self.assertTrue(serializer.get_is_owner(image))

        serializer = FileSerializer(image, context={'user': UserF.create()})
        self.assertFalse(serializer.get_is_owner(image))

    def test_get_image_url(self):
        image = ImageFileFactory.create()

        serializer = FileSerializer(image, context={'user': image.creator})
        self.assertEqual(serializer.get_url(image), image.image.url)

    def test_get_thumb_url(self):
        image = ImageFileFactory.create()

        serializer = FileSerializer(image, context={'user': image.creator})
        self.assertEqual(
            serializer.get_thumbnail_url(image),
            image.image.url + '.500x500_q85_crop.png'
        )

    def test_get_youtube_link(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(serializer.get_url(video), video.youtube_link)

    def test_get_youtube_thumb(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertIsNone(serializer.get_thumbnail_url(video))

    def test_get_video_file_type(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(serializer.get_type(video), 'VideoFile')
