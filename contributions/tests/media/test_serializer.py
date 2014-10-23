from django.test import TestCase
from users.tests.model_factories import UserF

from .model_factories import ImageFileFactory, VideoFileFactory
from contributions.serializers import FileSerializer


class FileSerializerTest(TestCase):
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

    def test_get_youtube_link(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(serializer.get_url(video), video.swf_link)

    def test_get_video_file_type(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(serializer.get_type(video), 'VideoFile')
