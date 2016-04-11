"""Tests for serializers of contributions (media files)."""

import os
import glob

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from geokey.users.tests.model_factories import UserFactory

from .model_factories import (
    ImageFileFactory,
    VideoFileFactory,
    AudioFileFactory
)
from geokey.contributions.serializers import FileSerializer


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
        self.assertTrue(serializer.get_isowner(image))

        serializer = FileSerializer(
            image, context={'user': UserFactory.create()})
        self.assertFalse(serializer.get_isowner(image))

        serializer = FileSerializer(image, context={'user': AnonymousUser()})
        self.assertFalse(serializer.get_isowner(image))

    def test_get_image_url(self):
        image = ImageFileFactory.create()

        serializer = FileSerializer(image, context={'user': image.creator})
        self.assertEqual(serializer.get_url(image), image.image.url)

    def test_get_thumb_url(self):
        image = ImageFileFactory.create()

        serializer = FileSerializer(image, context={'user': image.creator})
        self.assertEqual(
            serializer.get_thumbnail_url(image),
            image.image.url + '.300x300_q85_crop.png'
        )

    def test_get_youtube_link(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(serializer.get_url(video), video.youtube_link)

    def test_get_youtube_no_thumb(self):
        video = VideoFileFactory.create(**{'youtube_id': 'asadf'})

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(
            serializer.get_thumbnail_url(video),
            '/static/img/play.png'
        )

    def test_get_youtube_thumb(self):
        video = VideoFileFactory.create(**{'youtube_id': '14emk_jPnrI'})

        serializer = FileSerializer(video, context={'user': video.creator})

        self.assertNotEqual(
            serializer.get_thumbnail_url(video),
            '/static/img/play.png'
        )

    def test_get_video_file_type(self):
        video = VideoFileFactory.create()

        serializer = FileSerializer(video, context={'user': video.creator})
        self.assertEqual(serializer.get_file_type(video), 'VideoFile')

    def test_get_audio(self):
        audio = AudioFileFactory.create()

        serializer = FileSerializer(audio, context={'user': audio.creator})
        self.assertEqual(
            serializer.get_thumbnail_url(audio),
            '/static/img/play.png'
        )
